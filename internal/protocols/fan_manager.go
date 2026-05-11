package protocols

import (
	"context"
	"log"
	"time"

	"cc_hive/cc_empire/core"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// FanProfile defines the persistent state of a user interacting with the models.
type FanProfile struct {
	UserID            string    `bson:"user_id"`
	Tier              string    `bson:"tier"`
	NSFWWarnings      int       `bson:"nsfw_warnings"`
	IsBlocked         bool      `bson:"is_blocked"`
	FinanceSoftBan    bool      `bson:"finance_soft_ban"`
	InteractionCount  int       `bson:"interaction_count"`
	LastSeen          time.Time `bson:"last_seen"`
	CreatedAt         time.Time `bson:"created_at"`
	RelationshipDepth string    `bson:"relationship_depth"`
}

// FanManager handles MongoDB operations for user profiles and safety incidents.
type FanManager struct {
	Collection *mongo.Collection
}

// NewFanManager initializes the connection to the fan_profiles collection.
func NewFanManager() *FanManager {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, err := mongo.Connect(ctx, options.Client().ApplyURI(core.Settings.DatabaseURL))
	if err != nil {
		log.Printf("❌ FanManager Connection Error: %v", err)
	}

	collection := client.Database("CyberChest_Hive").Collection("fan_profiles")
	return &FanManager{Collection: collection}
}

// FetchProfile retrieves a user profile or creates a default one if it doesn't exist.
func (fm *FanManager) FetchProfile(ctx context.Context, userID string) (*FanProfile, error) {
	var profile FanProfile
	filter := bson.M{"user_id": userID}

	err := fm.Collection.FindOne(ctx, filter).Decode(&profile)
	if err == mongo.ErrNoDocuments {
		profile = FanProfile{
			UserID:            userID,
			Tier:              "free",
			RelationshipDepth: "Initial Contact",
			CreatedAt:         time.Now().UTC(),
			LastSeen:          time.Now().UTC(),
		}
		_, err = fm.Collection.InsertOne(ctx, profile)
		return &profile, err
	}
	return &profile, err
}

// UpdateSafetyMetrics persists NSFW warnings or block status.
func (fm *FanManager) UpdateSafetyMetrics(ctx context.Context, userID string, warnings int, blocked bool) error {
	filter := bson.M{"user_id": userID}
	update := bson.M{
		"$set": bson.M{
			"nsfw_warnings": warnings,
			"is_blocked":    blocked,
			"last_seen":     time.Now().UTC(),
		},
	}
	_, err := fm.Collection.UpdateOne(ctx, filter, update)
	return err
}

// MarkFinanceBan sets the soft ban for financial protection.
func (fm *FanManager) MarkFinanceBan(ctx context.Context, userID string) error {
	filter := bson.M{"user_id": userID}
	update := bson.M{
		"$set": bson.M{
			"tier":             "free_empathy_only",
			"finance_soft_ban": true,
			"last_seen":        time.Now().UTC(),
		},
	}
	_, err := fm.Collection.UpdateOne(ctx, filter, update)
	return err
}

func (fm *FanManager) MarkTransaction(ctx context.Context, userID string, amount float64, depth string) error {
	filter := bson.M{"user_id": userID}
	update := bson.M{
		"$inc": bson.M{"interaction_count": 1},
		"$set": bson.M{
			"relationship_depth": depth,
			"last_seen":          time.Now().UTC(),
		},
	}
	_, err := fm.Collection.UpdateOne(ctx, filter, update)
	return err
}

// ApplyIntimacyDecay checks for stale users and degrades their relationship tier.
// This replaces the logic from intimacy_tracker.py.
func (fm *FanManager) ApplyIntimacyDecay(ctx context.Context) (int64, error) {
	// Users who haven't been seen in 72 hours drop one level.
	cutoff := time.Now().AddDate(0, 0, -3).UTC()

	// 1. "Inner Circle" drops to "Dedicated Fan"
	filterInner := bson.M{
		"last_seen":          bson.M{"$lt": cutoff},
		"relationship_depth": "Inner Circle",
	}
	updateInner := bson.M{"$set": bson.M{"relationship_depth": "Dedicated Fan"}}
	resInner, err := fm.Collection.UpdateMany(ctx, filterInner, updateInner)
	if err != nil {
		return 0, err
	}

	// 2. "Dedicated Fan" drops to "Initial Contact"
	filterFan := bson.M{
		"last_seen":          bson.M{"$lt": cutoff},
		"relationship_depth": "Dedicated Fan",
	}
	updateFan := bson.M{"$set": bson.M{"relationship_depth": "Initial Contact"}}
	resFan, err := fm.Collection.UpdateMany(ctx, filterFan, updateFan)
	if err != nil {
		return resInner.ModifiedCount, err
	}

	total := resInner.ModifiedCount + resFan.ModifiedCount
	if total > 0 {
		log.Printf("📉 INTIMACY DECAY: %d relationships have grown cold due to absence.", total)
	}
	return total, nil
}
