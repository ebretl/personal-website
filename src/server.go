package main

import (
    "fmt"
    "net/http"
    "io/ioutil"
    "strings"
    "os/exec"
    "time"
)


var top_songs []string

func handler(w http.ResponseWriter, r *http.Request) {
    resp := "<html><head></head><body>"
    for i, song := range top_songs {
        resp += fmt.Sprintf("<p>%v) %v", i+1, song)
    }
    resp += "</body></html>"
    fmt.Fprintf(w, resp)
}

func refresh_top_songs() {
    exec.Command("python3", "songs/get_top_songs.py").Run()
    bytes, _ := ioutil.ReadFile("songs/top_songs.txt")
    top_songs = strings.Split(string(bytes), "\n")
    top_songs = top_songs[:len(top_songs)-1]
    fmt.Println("refreshed top songs list")
}

func song_refresher_thread() {
    for {
        refresh_top_songs()
        time.Sleep(time.Minute * 10)
    }
}

func main() {
    go song_refresher_thread()

    http.HandleFunc("/", handler)
    port := ":8080"
    fmt.Println("serving", port)
    http.ListenAndServe(port, nil)
}
