package main

import (
    "fmt"
    "net/http"
)

func main() {
    http.Handle("/", http.FileServer(http.Dir("")))
    port := ":80"
    fmt.Println("serving", port)
    panic(http.ListenAndServe(port, nil))
}
