package tunnel

import (
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

const (
	HeartbeatInterval = 30 * time.Second
	ReconnectDelay    = 5 * time.Second
	HandshakeTimeout  = 10 * time.Second
	WriteTimeout      = 10 * time.Second
	MaxReconnectDelay = 60 * time.Second
)

type MessageType string

const (
	TypeHeartbeat    MessageType = "heartbeat"
	TypeHeartbeatACK MessageType = "heartbeat_ack"
	TypeQuery        MessageType = "query"
	TypeResult       MessageType = "result"
	TypeError        MessageType = "error"
)

type Message struct {
	RequestID string      `json:"request_id"`
	Type      MessageType `json:"type"`
	TenantID  string      `json:"tenant_id"`
	Payload   string      `json:"payload"`
	HMAC      string      `json:"hmac"`
	Timestamp int64       `json:"timestamp"`
}

type QueryHandler func(query string, requestID string) (string, error)

type Client struct {
	tenantID     string
	secret       string
	guardianURL  string
	conn         *websocket.Conn
	queryHandler QueryHandler
	done         chan struct{}

	// writeMu guards c.conn.WriteMessage. gorilla/websocket connections
	// are NOT safe for concurrent writes — heartbeat() runs on its own
	// goroutine while handleMessage() is spawned per incoming message
	// (via `go c.handleMessage(msg)`), and both can call send() at the
	// same time. Without this lock, two goroutines writing to the same
	// connection simultaneously can interleave/corrupt frames on the wire.
	writeMu sync.Mutex
}

func NewClient(
	tenantID string,
	secret string,
	guardianURL string,
	handler QueryHandler,
) *Client {
	return &Client{
		tenantID:     tenantID,
		secret:       secret,
		guardianURL:  guardianURL,
		queryHandler: handler,
		done:         make(chan struct{}),
	}
}

func (c *Client) Start(ctx context.Context) {
	delay := ReconnectDelay
	for {
		select {
		case <-ctx.Done():
			log.Println("Tunnel client shutting down")
			return
		default:
		}

		log.Printf("[SENTRY] Connecting to Guardian at %s...", c.guardianURL)
		if err := c.connect(ctx); err != nil {
			log.Printf("[SENTRY] Connection failed: %v. Retrying in %s", err, delay)
			select {
			case <-ctx.Done():
				return
			case <-time.After(delay):
				delay = min(delay*2, MaxReconnectDelay)
			}
			continue
		}

		// Reset delay on successful connection
		delay = ReconnectDelay
		log.Printf("[SENTRY] Connected to Guardian successfully (tenant=%s)", c.tenantID)
		c.run(ctx)
		log.Println("[SENTRY] Connection lost. Reconnecting...")
	}
}

func (c *Client) connect(ctx context.Context) error {
	url := fmt.Sprintf("%s/%s", c.guardianURL, c.tenantID)

	dialer := websocket.Dialer{
		HandshakeTimeout: HandshakeTimeout,
	}

	header := http.Header{}
	conn, _, err := dialer.DialContext(ctx, url, header)
	if err != nil {
		return fmt.Errorf("dial failed: %w", err)
	}

	c.conn = conn
	return nil
}

func (c *Client) run(ctx context.Context) {
	defer c.conn.Close()

	// Start heartbeat
	go c.heartbeat(ctx)

	// Read messages
	for {
		select {
		case <-ctx.Done():
			return
		default:
		}

		_, raw, err := c.conn.ReadMessage()
		if err != nil {
			log.Printf("[SENTRY] Read error: %v", err)
			return
		}

		var msg Message
		if err := json.Unmarshal(raw, &msg); err != nil {
			log.Printf("[SENTRY] Failed to parse message: %v", err)
			continue
		}

		log.Printf("[SENTRY] <- received type=%s request_id=%s", msg.Type, msg.RequestID)
		go c.handleMessage(msg)
	}
}

func (c *Client) handleMessage(msg Message) {
	switch msg.Type {
	case TypeHeartbeatACK:
		log.Printf("[SENTRY] Heartbeat ACK received: request_id=%s", msg.RequestID)

	case TypeQuery:
		start := time.Now()
		log.Printf("[SENTRY] Query received: request_id=%s sql=%q", msg.RequestID, msg.Payload)

		result, err := c.queryHandler(msg.Payload, msg.RequestID)
		elapsed := time.Since(start)

		if err != nil {
			log.Printf(
				"[SENTRY] Query FAILED: request_id=%s duration=%s error=%v",
				msg.RequestID, elapsed, err,
			)
			c.sendError(msg.RequestID, err.Error())
			return
		}

		log.Printf(
			"[SENTRY] Query OK: request_id=%s duration=%s result_bytes=%d",
			msg.RequestID, elapsed, len(result),
		)
		c.sendResult(msg.RequestID, result)

	default:
		log.Printf("[SENTRY] Unknown message type: %s", msg.Type)
	}
}

func (c *Client) heartbeat(ctx context.Context) {
	ticker := time.NewTicker(HeartbeatInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			msg := Message{
				Type:      TypeHeartbeat,
				TenantID:  c.tenantID,
				Timestamp: time.Now().Unix(),
			}
			if err := c.send(msg); err != nil {
				log.Printf("[SENTRY] Heartbeat failed: %v", err)
				return
			}
			log.Println("[SENTRY] Heartbeat sent")
		}
	}
}

func (c *Client) sendResult(requestID string, payload string) {
	msg := Message{
		RequestID: requestID,
		Type:      TypeResult,
		TenantID:  c.tenantID,
		Payload:   payload,
		Timestamp: time.Now().Unix(),
	}
	if err := c.send(msg); err != nil {
		log.Printf("[SENTRY] Failed to send result: %v", err)
	} else {
		log.Printf("[SENTRY] -> sent result request_id=%s", requestID)
	}
}

func (c *Client) sendError(requestID string, errMsg string) {
	msg := Message{
		RequestID: requestID,
		Type:      TypeError,
		TenantID:  c.tenantID,
		Payload:   errMsg,
		Timestamp: time.Now().Unix(),
	}
	if err := c.send(msg); err != nil {
		log.Printf("[SENTRY] Failed to send error: %v", err)
	} else {
		log.Printf("[SENTRY] -> sent error request_id=%s", requestID)
	}
}

func (c *Client) sign(msg Message) string {
	payload := fmt.Sprintf("%s:%s:%s:%s:%d", msg.RequestID, msg.Type, msg.TenantID, msg.Payload, msg.Timestamp)
	h := hmac.New(sha256.New, []byte(c.secret))
	h.Write([]byte(payload))
	return hex.EncodeToString(h.Sum(nil))
}

func (c *Client) send(msg Message) error {
	msg.HMAC = c.sign(msg)
	data, err := json.Marshal(msg)
	if err != nil {
		return fmt.Errorf("marshal failed: %w", err)
	}

	c.writeMu.Lock()
	defer c.writeMu.Unlock()

	c.conn.SetWriteDeadline(time.Now().Add(WriteTimeout))
	return c.conn.WriteMessage(websocket.TextMessage, data)
}
func min(a, b time.Duration) time.Duration {
	if a < b {
		return a
	}
	return b
}
