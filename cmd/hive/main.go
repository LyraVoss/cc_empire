package main

import (
	"cc_hive/cc_empire/core"
	"cc_hive/cc_empire/core/protocols"
	"context"
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
)

func main() {
	// Initialize and validate configuration
	core.LoadConfig()

	// Initialize HiveMind logic
	gin.SetMode(gin.ReleaseMode)
	r := gin.Default()

	// Start Unified Heartbeat System
	hb := protocols.NewHiveHeartbeat()
	hb.Start(context.Background())

	// Endpoints
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":      "online",
			"environment": core.Settings.Environment,
			"engine":      "Go-Native",
		})
	})

	fmt.Printf("🧠 Hive Mind (Go) active on port %d\n", core.Settings.Port)
	r.Run(fmt.Sprintf(":%d", core.Settings.Port))
}
