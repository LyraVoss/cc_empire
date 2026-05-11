package protocols

import (
	"context"
	"fmt"
	"log"
	"strings"
	"time"

	"cc_hive/cc_empire/core"
	"cc_hive/cc_empire/core/models"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type LyraExecutive struct {
	AdminID    string
	Collection *mongo.Collection
	AuditColl  *mongo.Collection
	CircleColl *mongo.Collection
}

func NewLyraExecutive() *LyraExecutive {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, err := mongo.Connect(ctx, options.Client().ApplyURI(core.Settings.DatabaseURL))
	if err != nil {
		log.Printf("❌ Executive Connection Error: %v", err)
	}

	db := client.Database("CyberChest_Hive")
	return &LyraExecutive{
		AdminID:    "LYRA_MODEL_0",
		Collection: db.Collection("model_profiles"),
		AuditColl:  db.Collection("audit_logs"),
		CircleColl: db.Collection("social_circles"),
	}
}

// AuditFleet scans active models for profitability margins.
func (l *LyraExecutive) AuditFleet(ctx context.Context) ([]map[string]interface{}, error) {
	cursor, err := l.Collection.Find(ctx, bson.M{"status": "Active"})
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var fleet []models.ModelProfile
	if err := cursor.All(ctx, &fleet); err != nil {
		return nil, err
	}

	report := make([]map[string]interface{}, 0)
	for _, m := range fleet {
		margin := 0.0
		if m.PerformanceMetrics.TotalRevenue > 0 {
			margin = (m.PerformanceMetrics.TotalRevenue - m.PerformanceMetrics.ApiCosts) / m.PerformanceMetrics.TotalRevenue
		}

		status := "UNDERPERFORMING"
		if margin > 0.3 {
			status = "HEALTHY"
		}

		report = append(report, map[string]interface{}{
			"model_name": m.Name,
			"margin":     fmt.Sprintf("%.2f%%", margin*100),
			"status":     status,
		})
	}
	return report, nil
}

// InitiateReproduction spawns a new worker if the hive is healthy.
func (l *LyraExecutive) InitiateReproduction(ctx context.Context, name, region string) (string, error) {
	// Logic check: Fleet health
	report, _ := l.AuditFleet(ctx)
	for _, r := range report {
		if r["status"] == "UNDERPERFORMING" {
			return "", fmt.Errorf("reproduction paused: optimization required")
		}
	}

	circleID, _ := l.determineSocialCircle(ctx, region)

	newModel := models.ModelProfile{
		ModelID:        fmt.Sprintf("WORKER_%s_%d", strings.ToUpper(name), time.Now().Unix()),
		Name:           name,
		Status:         "Active",
		Region:         region,
		SocialCircleID: circleID,
		CreatedAt:      time.Now().UTC(),
	}

	_, err := l.Collection.InsertOne(ctx, newModel)
	if err != nil {
		return "", err
	}

	l.AuditColl.InsertOne(ctx, models.AuditLog{
		ActorID:   l.AdminID,
		Action:    "SPAWN_WORKER",
		Timestamp: time.Now().UTC(),
	})

	return newModel.ModelID, nil
}

func (l *LyraExecutive) determineSocialCircle(ctx context.Context, region string) (string, error) {
	// Simplified: Find circle with capacity < 5 or create new
	return "CIRCLE_" + strings.ToUpper(region), nil
}
