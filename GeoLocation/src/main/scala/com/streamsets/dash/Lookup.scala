package com.streamsets.dash

import scalaj.http.{Http, HttpResponse}

//https://github.com/ruippeixotog/scala-scraper#core-model
import net.ruippeixotog.scalascraper.browser.JsoupBrowser
import net.ruippeixotog.scalascraper.dsl.DSL._
import net.ruippeixotog.scalascraper.dsl.DSL.Extract._

object Lookup {
  def main(args: Array[String]) {
  }

  def ip(ipAddress: String, query: String = "N/A") = {
    var response = "Ok"

    val httpRequest = "https://www.netip.de/123/search?query=" + ipAddress
    val httpResponse: HttpResponse[String] = Http(httpRequest).asString

    if (httpResponse.code == 200) {
      val body = httpResponse.body

//      println(body)

      val countryPattern = """(?<=Country: )(.*)(?=&nbsp;)""".r
      val statePattern = """(?<=State/Region: )(.*)(?=<br />)""".r
      val cityPattern = """(?<=City: )(.*)""".r
      var country = ""
      var state = ""
      var city = ""
      var country_code = ""

      countryPattern.findAllIn(body).matchData foreach {
        m => country = m.group(1)
      }
      statePattern.findAllIn(body).matchData foreach {
        m => state = m.group(1)
          state = state.trim
      }
      cityPattern.findAllIn(body).matchData foreach {
        m => city = m.group(1)
      }

      if (country != "") {
        val country_values = country.split("-").map(_.trim)
        country_code = country_values(0)
        country      = country_values(1)
      }

      response = query.toLowerCase match {
        case "country"      => country
        case "country code" => country_code
        case "state"        => state
        case "city"         => city
        case _              => "Country:" + country + "-Code:" + country_code + "-State:" + state + "-City:" + city
      }

      println("Country: " + country)
      println("Country Code: " + country_code)
      println("State: " + state)
      println("City: " + city)

    } else {
    }

    response
  }

  def ip2(ipAddress: String, query: String = "N/A") = {
    var response = "Ok"
    try {
      val httpRequest = "https://www.netip.de/123/search?query=" + ipAddress
      val browser = JsoupBrowser()
      //val doc = browser.get("https://github.com/ruippeixotog/scala-scraper/blob/master/core/src/test/resources/example.html")
      val doc = browser.get(httpRequest)

      val countryPattern = """(?<=Country: )(.*)(?= State)""".r
      val statePattern = """(?<=State/Region: )(.*)(?= City)""".r
      val cityPattern = """(?<=City: )(.*)""".r
      var country = ""
      var state = ""
      var city = ""
      var country_code = ""

      val text = doc >> texts("p")
      text.foreach { t =>
        countryPattern.findAllIn(t).matchData foreach {
          m => country = m.group(1)
        }
        statePattern.findAllIn(t).matchData foreach {
          m => state = m.group(1)
        }
        cityPattern.findAllIn(t).matchData foreach {
          m => city = m.group(1)
        }
      }

      if (country != "") {
        val country_values = country.split("-").map(_.trim)
        country_code = country_values(0)
        country      = country_values(1)
      }

      response = query.toLowerCase match {
        case "country"      => country
        case "country code" => country_code
        case "state"        => state
        case "city"         => city
        case _              => "Country:" + country + "-Country Code:" + country_code + "-State:" + state + "-City:" + city
      }

      println("Country: " + country)
      println("Country Code: " + country_code)
      println("State: " + state)
      println("City: " + city)
    } catch {
      case e: Exception =>
        response = "Error: " + e
    }

    println("=============== Response  ===============")
    println(response)
    response
  }

}
