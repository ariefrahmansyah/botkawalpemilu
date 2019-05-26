package main

import (
	"log"
	"os"

	"github.com/dghubble/go-twitter/twitter"
	"github.com/dghubble/oauth1"
)

var twitterClient *twitter.Client

func mustInitTwitterClient() {
	twitterConsumerAPIKey := os.Getenv("TWITTER_CONSUMER_API_KEY")
	if twitterConsumerAPIKey == "" {
		log.Fatal("$TWITTER_CONSUMER_API_KEY must be set")
	}

	twitterConsumerAPISecret := os.Getenv("TWITTER_CONSUMER_API_SECRET")
	if twitterConsumerAPISecret == "" {
		log.Fatal("$TWITTER_CONSUMER_API_SECRET must be set")
	}

	twitterAccessToken := os.Getenv("TWITTER_ACCESS_TOKEN")
	if twitterAccessToken == "" {
		log.Fatal("$TWITTER_ACCESS_TOKEN must be set")
	}

	twitterAccessSecret := os.Getenv("TWITTER_ACCESS_SECRET")
	if twitterAccessSecret == "" {
		log.Fatal("$TWITTER_ACCESS_SECRET must be set")
	}

	oauthConfig := oauth1.NewConfig(twitterConsumerAPIKey, twitterConsumerAPISecret)
	oauthToken := oauth1.NewToken(twitterAccessToken, twitterAccessSecret)
	oauthClient := oauthConfig.Client(oauth1.NoContext, oauthToken)

	twitterClient = twitter.NewClient(oauthClient)
}
