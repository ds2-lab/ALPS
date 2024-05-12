// consuming-api/simple/main.go
package main

import (
    "fmt"
    //"io/ioutil"
    "net/http"
    "time"
    "bytes"
    "encoding/json"
    "os"
    "log"
    "bufio"
    "strconv"
    "strings"
    "io/ioutil"
    "sync"
)

type Data struct{
	Id	string
	N	string
	Job	string
	St	int
	Port	string
}


func GetTrace(path string)[]Data{
	file, err := os.Open(path)
	if err != nil{
		log.Fatal(err)
	}
	defer file.Close()
	scanner := bufio.NewScanner(file)
	scanner.Split(bufio.ScanLines)
	var txtlines []string
	for scanner.Scan(){
		txtlines = append(txtlines, scanner.Text())
	}
	trace := []Data{}
	var s []string
	var i1 int
	var newData Data
	for _,eachline := range txtlines{
		s = strings.Split(eachline," ")
		i1, _ = strconv.Atoi(s[3])
		newData = Data{s[0],s[1],s[2],int(0.21*float64(i1)), s[4]}
		//newData = Data{s[0],s[1],s[2],3*i1,s[4]}
		trace = append(trace, newData)
	}
	return trace
}

func Post(cli *http.Client, d Data,wg *sync.WaitGroup){
	defer wg.Done()
	m := map[string]string{"n":d.N,"id":d.Id,"job":d.Job}
	b := new(bytes.Buffer)
        json.NewEncoder(b).Encode(m)
	resp, err := cli.Post("http://127.0.0.1:"+d.Port+"/run/"+d.Job,"application/json", b)
	if err != nil {
                fmt.Printf("Error %s", err)
                return
        }
        defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	fmt.Printf("Body : %s", body)
}

func main() {
    	trace := GetTrace("exp")
	tr := &http.Transport{
		MaxIdleConns:       102400,
		IdleConnTimeout:    30 * time.Second,
		DisableCompression: true,
	}
	wg := sync.WaitGroup{}
	c := &http.Client{Transport: tr}
    	//c := http.Client{Timeout: time.Duration(1) * time.Second}
	for _,t := range(trace){
		wg.Add(1)
		time.Sleep(time.Duration(t.St)*time.Millisecond)
		go Post(c, t, &wg)
        }
	wg.Wait()
}