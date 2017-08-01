/**
 * Copyright 2017, Google, Inc.
 * Licensed under the Apache License, Version 2.0 (the `License`);
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an `AS IS` BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package main

import (
	"fmt"
	"net/http"
	"os"
)

func mainHandler(w http.ResponseWriter, r *http.Request) {
	msg := os.Getenv("MSG")
	if msg == "" {
		msg = "woohoo automation\n"
	}
	fmt.Fprint(w, msg)
}

func versionHandler(w http.ResponseWriter, r *http.Request) {
	version := os.Getenv("CONTAINER_DIGEST") // port string
	if version == "" {
		version = "unknown"
	}
	fmt.Fprint(w, version)
}

func main() {

	port := os.Getenv("PORT") // port string
	if port == "" {
		port = "8080"
	}
	http.HandleFunc("/", mainHandler)
	http.HandleFunc("/version/", versionHandler)

	fmt.Printf("Running server on port: %s\nType Ctr-c to shutdown server.\n", port)
	http.ListenAndServe(":"+port, nil)
}
