package protocols

import (
	"fmt"
	"sync"
)

// BrainFactory manages the lifecycle of multiple BrainEngine instances.
type BrainFactory struct {
	engines map[string]*BrainEngine
	mu      sync.RWMutex
}

// NewBrainFactory initializes a new registry for Hive Mind personas.
func NewBrainFactory() *BrainFactory {
	return &BrainFactory{
		engines: make(map[string]*BrainEngine),
	}
}

// GetEngine retrieves an existing BrainEngine or initializes a new one.
// This ensures DNA locking and router setup only happens once per model.
func (f *BrainFactory) GetEngine(modelID string) (*BrainEngine, error) {
	// Read lock for quick checks
	f.mu.RLock()
	engine, exists := f.engines[modelID]
	f.mu.RUnlock()

	if exists {
		return engine, nil
	}

	// Write lock for initialization
	f.mu.Lock()
	defer f.mu.Unlock()

	// Double-check existence after acquiring write lock
	if engine, exists := f.engines[modelID]; exists {
		return engine, nil
	}

	newEngine, err := NewBrainEngine(modelID)
	if err != nil {
		return nil, fmt.Errorf("failed to build brain for %s: %v", modelID, err)
	}

	f.engines[modelID] = newEngine
	return newEngine, nil
}
