package com.streamsets.dash

object Demo {
  def main(args: Array[String]) {
    printStrings("Hello", "World", "Scala");
  }

  def printStrings( args:String* ) = {
    var i : Int = 0;

    for( arg <- args ){
      println("Arg value[" + i + "] = " + arg );
      i = i + 1;
    }
  }

  def hello(name: String = "Transformer") = {
    "Hello " + name
  }
}
