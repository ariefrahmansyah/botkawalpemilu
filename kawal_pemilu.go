package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
)

const (
	kawalPemiluAPIEndpoint = "https://kawal-c1.appspot.com/api/c/0"
)

type kawalPemiluData struct {
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

func getKawalPemiluData() (kawalPemiluData, error) {
	resp, err := http.Get(kawalPemiluAPIEndpoint)
	if err != nil {
		return kawalPemiluData{}, fmt.Errorf("Fail getting data from KawalPemilu: %s", err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return kawalPemiluData{}, fmt.Errorf("Fail reading data from KawalPemilu: %s", err)
	}

	var data kawalPemiluData
	if err := json.Unmarshal(body, &data); err != nil {
		return kawalPemiluData{}, fmt.Errorf("Fail parse data from KawalPemilu: %s", err)
	}

	return data, nil
}
