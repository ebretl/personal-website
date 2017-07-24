package main

import (
    "fmt"
    "net/http"
    "io/ioutil"
)

func handler(w http.ResponseWriter, r *http.Request) {
    bytes, _ := ioutil.ReadFile("top_songs.txt")
    fmt.Fprintf(w, string(bytes))
}

func main() {
    http.HandleFunc("/", handler)
    http.ListenAndServe(":80", nil)
}
