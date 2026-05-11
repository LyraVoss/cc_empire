package neural_map

import (
	"context"
	"log"
	"time"

	"cc_hive/cc_empire/core"

	"github.com/sashabaranov/go-openai"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// MemoryDocument represents a single memory entry in MongoDB.
type MemoryDocument struct {
	UserID    string    `bson:"user_id"`
	ModelID   string    `bson:"model_id"`
	Content   string    `bson:"content"`
	Role      string    `bson:"role"`
	Embedding []float32 `bson:"embedding"`
	Timestamp time.Time `bson:"timestamp"`
}

type NeuralMapRouter struct {
	ModelID      string
	Collection   *mongo.Collection
	OpenAIClient *openai.Client
}

// NewNeuralMapRouter initializes the MongoDB collection and OpenAI client.
func NewNeuralMapRouter(modelID string) *NeuralMapRouter {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, err := mongo.Connect(ctx, options.Client().ApplyURI(core.Settings.DatabaseURL))
	if err != nil {
		log.Printf("❌ NeuralMap MongoDB Error: %v", err)
	}

	collection := client.Database("CyberChest_Hive").Collection("long_term_memory")

	var oaClient *openai.Client
	if core.Settings.OpenAIApiKey != "" {
		oaClient = openai.NewClient(core.Settings.OpenAIApiKey)
	}

	return &NeuralMapRouter{
		ModelID:      modelID,
		Collection:   collection,
		OpenAIClient: oaClient,
	}
}

// getEmbedding generates a vector for the given text.
func (n *NeuralMapRouter) getEmbedding(ctx context.Context, text string) ([]float32, error) {
	if n.OpenAIClient == nil {
		return nil, nil
	}

	resp, err := n.OpenAIClient.CreateEmbeddings(ctx, openai.EmbeddingRequest{
		Input: []string{text},
		Model: openai.SmallEmbedding3,
	})
	if err != nil {
		return nil, err
	}

	return resp.Data[0].Embedding, nil
}

// SaveMemory persists an interaction to MongoDB with its vector embedding.
func (n *NeuralMapRouter) SaveMemory(ctx context.Context, userID, content, role string) error {
	vector, err := n.getEmbedding(ctx, content)
	if err != nil || vector == nil {
		return err
	}

	doc := MemoryDocument{
		UserID:    userID,
		ModelID:   n.ModelID,
		Content:   content,
		Role:      role,
		Embedding: vector,
		Timestamp: time.Now().UTC(),
	}

	_, err = n.Collection.InsertOne(ctx, doc)
	return err
}

// GetContext retrieves relevant past interactions using Atlas Vector Search.
func (n *NeuralMapRouter) GetContext(ctx context.Context, userID, queryText string) (string, error) {
	vector, err := n.getEmbedding(ctx, queryText)
	if err != nil || vector == nil {
		return "User context: Established connection.", nil
	}

	// MongoDB Atlas Vector Search Pipeline
	pipeline := mongo.Pipeline{
		{{Key: "$vectorSearch", Value: bson.D{
			{Key: "index", Value: core.Settings.MongoVectorIndexName},
			{Key: "path", Value: "embedding"},
			{Key: "queryVector", Value: vector},
			{Key: "numCandidates", Value: 100},
			{Key: "limit", Value: 3},
		}}},
		{{Key: "$match", Value: bson.D{
			{Key: "user_id", Value: userID},
			{Key: "model_id", Value: n.ModelID},
		}}},
	}

	cursor, err := n.Collection.Aggregate(ctx, pipeline)
	if err != nil {
		return "", err
	}
	defer cursor.Close(ctx)

	var results []MemoryDocument
	if err = cursor.All(ctx, &results); err != nil {
		return "", err
	}

	if len(results) == 0 {
		return "No specific past context found. Treat as a continuing warm connection.", nil
	}

	var contextStr string
	for _, res := range results {
		contextStr += res.Content + " "
	}

	return "Past interaction context: " + contextStr, nil
}
