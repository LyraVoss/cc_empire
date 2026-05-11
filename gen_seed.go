package main

import (
	"fmt"
	"log"

	"github.com/tyler-smith/go-bip39"
)

func main() {
	// Generate 256 bits of entropy for a 24-word mnemonic
	entropy, err := bip39.NewEntropy(256)
	if err != nil {
		log.Fatal(err)
	}

	mnemonic, err := bip39.NewMnemonic(entropy)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("=== YOUR SECURE MASTER SEED ===")
	fmt.Println(mnemonic)
	fmt.Println("===============================")
	fmt.Println("STORE THIS OFFLINE. DO NOT SHARE.")
}
