package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"

	"golang.org/x/text/number"

	"github.com/dghubble/go-twitter/twitter"
	"github.com/dghubble/oauth1"
	_ "github.com/heroku/x/hmetrics/onload"
	"github.com/julienschmidt/httprouter"
	"github.com/robfig/cron"
	"golang.org/x/text/language"
	"golang.org/x/text/message"
)

type kawalPemiluResponse struct {
	Children [][]interface{} `json:"children"`
	Data     map[string]struct {
		Summary struct {
			Candidate1 int `json:"pas1"`
			Candidate2 int `json:"pas2"`
			Cakupan    int `json:"cakupan"` // # of TPS uploaded to KawalPemilu
			Pending    int `json:"pending"` // # of TPS uploaded to KawalPemilu but not processed yet
		} `json:"sum"`
	} `json:"data"`
}

var status string

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		log.Fatal("$PORT must be set")
	}

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

	tweetInterval := os.Getenv("TWEET_INTERVAL")
	if tweetInterval == "" {
		tweetInterval = "15m"
	}
	interval := fmt.Sprintf("@every %s", tweetInterval)

	botKawalPemiluPingEndpoint := "https://botkawalpemilu.herokuapp.com/ping"
	kawalPemiluAPIEndpoint := "https://kawal-c1.appspot.com/api/c/0"

	oauthConfig := oauth1.NewConfig(twitterConsumerAPIKey, twitterConsumerAPISecret)
	oauthToken := oauth1.NewToken(twitterAccessToken, twitterAccessSecret)
	oauthClient := oauthConfig.Client(oauth1.NoContext, oauthToken)

	twitterClient := twitter.NewClient(oauthClient)

	c := cron.New()
	c.AddFunc("@every 5m", func() {
		resp, err := http.Get(botKawalPemiluPingEndpoint)
		if err != nil {
			log.Printf("Fail pinging botkawalpemilu: %s", err)
			return
		}
		defer resp.Body.Close()
	})
	c.AddFunc(interval, func() {
		log.Printf("Getting new data...")

		resp, err := http.Get(kawalPemiluAPIEndpoint)
		if err != nil {
			log.Printf("Fail getting response from KawalPemilu: %s", err)
			return
		}
		defer resp.Body.Close()

		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			log.Printf("Fail reading response from KawalPemilu: %s", err)
			return
		}

		var response kawalPemiluResponse
		if err := json.Unmarshal(body, &response); err != nil {
			log.Printf("Fail parse response from KawalPemilu: %s", err)
			return
		}

		totalCandidate1, totalCandidate2 := 0, 0
		tpsProcessed := 0

		for _, data := range response.Data {
			totalCandidate1 += data.Summary.Candidate1
			totalCandidate2 += data.Summary.Candidate2

			tpsProcessed += data.Summary.Cakupan - data.Summary.Pending
		}

		total := totalCandidate1 + totalCandidate2

		percentageCandidate1 := float64(totalCandidate1) / float64(total)
		percentageCandidate2 := float64(totalCandidate2) / float64(total)

		var totalTPS float64
		for _, child := range response.Children {
			totalTPS += child[2].(float64)
		}

		percentageTPS := float64(tpsProcessed) / float64(totalTPS)

		log.Println("Total TPS", totalTPS)
		log.Println("Total TPS Processed", tpsProcessed)
		log.Println("Percentage TPS Processed", percentageTPS)

		p := message.NewPrinter(language.Dutch)

		newStatus := p.Sprintf("Jokowi-Amin: %d (%d)\nPrabowo-Sandi: %d (%d)\n\nTotal TPS: %d dari %d (%d)\n\n@KawalPemilu2019 #PantauFotoUpload #SaveOurDemocracy",
			number.Decimal(totalCandidate1),
			number.Percent(percentageCandidate1, number.MaxFractionDigits(3)),
			number.Decimal(totalCandidate2),
			number.Percent(percentageCandidate2, number.MaxFractionDigits(3)),
			number.Decimal(tpsProcessed),
			number.Decimal(totalTPS),
			number.Percent(percentageTPS, number.MaxFractionDigits(3)),
		)

		if newStatus != status {
			log.Printf("Tweeting: %s", newStatus)

			// Get last status ID
			user, _, _ := twitterClient.Users.Show(&twitter.UserShowParams{
				ScreenName: "botkawalpemilu",
			})

			lastStatusID := user.Status.ID

			// Send a Tweet
			_, _, err = twitterClient.Statuses.Update(newStatus, &twitter.StatusUpdateParams{InReplyToStatusID: lastStatusID})
			if err != nil {
				log.Printf("Updating status error: %s", err)
				return
			}
			// _ = twitterClient
		}

		status = newStatus
	})
	c.Start()
	defer c.Stop()

	router := httprouter.New()

	router.GET("/ping", pingHandler)
	router.GET("/status", statusHandler)

	log.Printf("Listening on port: %s", port)
	log.Fatal(http.ListenAndServe(fmt.Sprintf(":%s", port), router))
}

func pingHandler(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
	w.Write([]byte("pong"))
}

func statusHandler(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
	w.Write([]byte(status))
}
