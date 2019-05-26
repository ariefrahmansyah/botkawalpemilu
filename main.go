package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/dghubble/go-twitter/twitter"
	_ "github.com/heroku/x/hmetrics/onload"
	"github.com/julienschmidt/httprouter"
	"github.com/robfig/cron"
	"golang.org/x/text/language"
	"golang.org/x/text/message"
	"golang.org/x/text/number"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	tweetInterval := os.Getenv("TWEET_INTERVAL")
	if tweetInterval == "" {
		tweetInterval = "15m"
	}
	interval := fmt.Sprintf("@every %s", tweetInterval)

	mustInitTwitterClient()

	c := cron.New()

	// Ping botkawalpemilu app so Heroku's dyno stay active
	c.AddFunc("@every 5m", func() {
		botKawalPemiluPingEndpoint := "https://botkawalpemilu.herokuapp.com/ping"

		resp, err := http.Get(botKawalPemiluPingEndpoint)
		if err != nil {
			log.Printf("Fail pinging botkawalpemilu: %s", err)
			return
		}
		defer resp.Body.Close()
	})

	// Tweeting Kawal Pemilu update
	c.AddFunc(interval, func() {
		log.Printf("Getting new data...")

		kpData, err := getKawalPemiluData()
		if err != nil {
			log.Printf("Fail getting data from KawalPemilu: %s", err)
			return
		}

		totalCandidate1, totalCandidate2 := 0, 0
		tpsProcessed := 0

		for _, data := range kpData.Data {
			totalCandidate1 += data.Summary.Candidate1
			totalCandidate2 += data.Summary.Candidate2

			tpsProcessed += data.Summary.Cakupan - data.Summary.Pending
		}

		total := totalCandidate1 + totalCandidate2

		percentageCandidate1 := float64(totalCandidate1) / float64(total)
		percentageCandidate2 := float64(totalCandidate2) / float64(total)

		var totalTPS float64
		for _, child := range kpData.Children {
			totalTPS += child[2].(float64)
		}

		percentageTPS := float64(tpsProcessed) / float64(totalTPS)

		log.Println("Total TPS", totalTPS)
		log.Println("Total TPS Processed", tpsProcessed)
		log.Println("Percentage TPS Processed", percentageTPS)

		p := message.NewPrinter(language.Dutch)

		newStatus := p.Sprintf("Jokowi-Amin: %d (%d)\nPrabowo-Sandi: %d (%d)\n\nTotal TPS: %d dari %d (%d)\n\n@KawalPemilu2019 #PantauFotoUpload",
			number.Decimal(totalCandidate1),
			number.Percent(percentageCandidate1, number.MaxFractionDigits(3)),
			number.Decimal(totalCandidate2),
			number.Percent(percentageCandidate2, number.MaxFractionDigits(3)),
			number.Decimal(tpsProcessed),
			number.Decimal(totalTPS),
			number.Percent(percentageTPS, number.MaxFractionDigits(3)),
		)

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
	})

	c.Start()
	defer c.Stop()

	router := httprouter.New()

	router.GET("/ping", pingHandler)

	log.Printf("Listening on port: %s", port)
	log.Fatal(http.ListenAndServe(fmt.Sprintf(":%s", port), router))
}

func pingHandler(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
	w.Write([]byte("pong"))
}
