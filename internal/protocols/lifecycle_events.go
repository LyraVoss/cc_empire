package protocols

import "log"

type LifecycleEngine struct {
	ModelID string
}

func NewLifecycleEngine(modelID string) *LifecycleEngine {
	return &LifecycleEngine{ModelID: modelID}
}

func (l *LifecycleEngine) TriggerEvent(event string) {
	log.Printf("✨ [Lifecycle] %s event for %s", event, l.ModelID)
}
