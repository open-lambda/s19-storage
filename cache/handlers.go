package main

import (
	"io"
	"net/http"
	"strconv"
	"time"
        "os"
        //"reflect"
        //"strings"
        "fmt"
	"github.com/aws/aws-sdk-go/aws/awserr"
	"github.com/aws/aws-sdk-go/service/s3"
)


var timestamp = 0
var cache_dict = make(map[string]*s3.GetObjectOutput)
var lru_dict = make(map[string]int)
var counter = 0

func NewSSLRedirectHandler(next http.Handler) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Scheme != "https" {
			dest := "https://" + r.Host + r.URL.Path
			if r.URL.RawQuery != "" {
				dest += "?" + r.URL.RawQuery
			}

			http.Redirect(w, r, dest, http.StatusTemporaryRedirect)
			return
		}

		next.ServeHTTP(w, r)
	}
}

type HostDispatchingHandler struct {
	hosts map[string]http.Handler
}

func NewHostDispatchingHandler() *HostDispatchingHandler {
	return &HostDispatchingHandler{
		hosts: make(map[string]http.Handler),
	}
}

func (h *HostDispatchingHandler) HandleHost(host string, handler http.Handler) {
	h.hosts[host] = handler
}

func (h *HostDispatchingHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	handler, ok := h.hosts[getHost(r)]
	if !ok {
		http.Error(w, "Not Found", http.StatusNotFound)
		return
	}

	handler.ServeHTTP(w, r)
}

func NewBasicAuthHandler(users []User, next http.Handler) http.HandlerFunc {
	m := make(map[string]string)
	for _, u := range users {
		m[u.Name] = u.Password
	}

	return func(w http.ResponseWriter, r *http.Request) {
		username, password, ok := r.BasicAuth()
		if !ok {
			challenge(w, r)
			return
		}

		p, ok := m[username]
		if !ok {
			challenge(w, r)
			return
		}

		if password != p {
			challenge(w, r)
			return
		}

		next.ServeHTTP(w, r)
	}
}

func NewWebsiteHandler(next http.Handler, cfg *s3.GetBucketWebsiteOutput) http.HandlerFunc {
	suffix := cfg.IndexDocument.Suffix

	return func(w http.ResponseWriter, r *http.Request) {
		path := r.URL.Path

		if path == "" || path[len(path)-1] == '/' {
			r.URL.Path += *suffix
		}

		next.ServeHTTP(w, r)
	}
}

func NewProxyHandler(proxy S3Proxy, prefix string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		path := r.URL.Path
		if prefix != "" {
			path = "/" + prefix + path
		}

                // check the cache
                CACHE_DIR := "/users/aarati_K/cache/"

                if r.Method == "PUT" {
		    fmt.Println("we know it's a put")
                    obj, err := proxy.Get(path)

                    if err != nil {
			if awsErr, ok := err.(awserr.Error); ok {
				switch awsErr.Code() {
				case s3.ErrCodeNoSuchBucket, s3.ErrCodeNoSuchKey:
					http.Error(w, err.Error(), http.StatusNotFound)
				default:
					http.Error(w, err.Error(), http.StatusUnauthorized)
				}
			} else {
				http.Error(w, err.Error(), http.StatusInternalServerError)
			}

			return
		    }

		    setHeader(w, "Cache-Control", s2s(obj.CacheControl))
		    setHeader(w, "Content-Disposition", s2s(obj.ContentDisposition))
		    setHeader(w, "Content-Encoding", s2s(obj.ContentEncoding))
		    setHeader(w, "Content-Language", s2s(obj.ContentLanguage))
		    setHeader(w, "Content-Length", i2s(obj.ContentLength))
		    setHeader(w, "Content-Range", s2s(obj.ContentRange))
		    setHeader(w, "Content-Type", s2s(obj.ContentType))
		    setHeader(w, "ETag", s2s(obj.ETag))
		    setHeader(w, "Expires", s2s(obj.Expires))
		    setHeader(w, "Last-Modified", t2s(obj.LastModified))
		    io.Copy(w, obj.Body)
                    return
                }


                // check whether this file in the cache directory
                timestamp += 1

                fmt.Println("==============================================")
                if obj, prs := cache_dict[path]; prs == true {
                    // TODO update the timestamp
                    // object cached
                    fmt.Println("Hit!")
                    fmt.Println(obj)
                    lru_dict[path] = timestamp
		    setHeader(w, "Cache-Control", s2s(obj.CacheControl))
		    setHeader(w, "Content-Disposition", s2s(obj.ContentDisposition))
		    setHeader(w, "Content-Encoding", s2s(obj.ContentEncoding))
		    setHeader(w, "Content-Language", s2s(obj.ContentLanguage))
		    setHeader(w, "Content-Length", i2s(obj.ContentLength))
		    setHeader(w, "Content-Range", s2s(obj.ContentRange))
		    setHeader(w, "Content-Type", s2s(obj.ContentType))
		    setHeader(w, "ETag", s2s(obj.ETag))
		    setHeader(w, "Expires", s2s(obj.Expires))
		    setHeader(w, "Last-Modified", t2s(obj.LastModified))
                    // TODO get the real content
                    in, _ := os.Open(fmt.Sprintf("%s%s", CACHE_DIR, path))
                    defer in.Close()
                    io.Copy(w, in)
                    return
                } else {
                    // object does *not* exist
                    fmt.Println("Miss!")
		    obj, err := proxy.Get(path)

                    if err != nil {
			if awsErr, ok := err.(awserr.Error); ok {
				switch awsErr.Code() {
				case s3.ErrCodeNoSuchBucket, s3.ErrCodeNoSuchKey:
					http.Error(w, err.Error(), http.StatusNotFound)
				default:
					http.Error(w, err.Error(), http.StatusUnauthorized)
				}
			} else {
				http.Error(w, err.Error(), http.StatusInternalServerError)
			}

			return
		    }

		    setHeader(w, "Cache-Control", s2s(obj.CacheControl))
		    setHeader(w, "Content-Disposition", s2s(obj.ContentDisposition))
		    setHeader(w, "Content-Encoding", s2s(obj.ContentEncoding))
		    setHeader(w, "Content-Language", s2s(obj.ContentLanguage))
		    setHeader(w, "Content-Length", i2s(obj.ContentLength))
		    setHeader(w, "Content-Range", s2s(obj.ContentRange))
		    setHeader(w, "Content-Type", s2s(obj.ContentType))
		    setHeader(w, "ETag", s2s(obj.ETag))
		    setHeader(w, "Expires", s2s(obj.Expires))
		    setHeader(w, "Last-Modified", t2s(obj.LastModified))
		    //io.Copy(w, obj.Body)

                    // TODO put it in cache, if not
                    // evict if full
                    counter += 1
                    if counter > 2 {
                        //find something to evict
                        least_time := 100000000
                        least_key := ""
                        for key := range lru_dict {
                            if lru_dict[key] < least_time{
                                least_time = lru_dict[key]
                                least_key = key
                            }
                        }
                        fmt.Println("!!!!!!!!!!To evict: ", least_key, ": ", least_time)
                        delete(lru_dict, least_key)
                        delete(cache_dict, least_key)
                    }

                    defer obj.Body.Close()
                    out, err := os.Create(fmt.Sprintf("%s%s", CACHE_DIR, path))
                    defer out.Close()
                    io.Copy(out, obj.Body)

                    in, err := os.Open(fmt.Sprintf("%s%s", CACHE_DIR, path))
                    defer in.Close()
                    io.Copy(w, in)
                    cache_dict[path] = obj
                    lru_dict[path] = timestamp
                    //fmt.Println(cache_dict[path])
                }
	}
}

func challenge(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("WWW-Authenticate", `Basic realm="`+getHost(r)+`"`)
	http.Error(w, "", http.StatusUnauthorized)
}

func getHost(r *http.Request) string {
	host := r.Header.Get("Host")
	if host == "" {
		host = r.Host
	}

	return host
}

func s2s(s *string) string {
	if s != nil {
		return *s
	} else {
		return ""
	}
}

func i2s(i *int64) string {
	if i != nil {
		return strconv.FormatInt(*i, 10)
	} else {
		return ""
	}
}

func t2s(t *time.Time) string {
	if t != nil {
		return t.UTC().Format(http.TimeFormat)
	} else {
		return ""
	}
}

func setHeader(w http.ResponseWriter, key, value string) {
	if value != "" {
		w.Header().Add(key, value)
	}
}
