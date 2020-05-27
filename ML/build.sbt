lazy val root = (project in file("."))
  .settings(
    name := "movie",
    version := "1.0",
    scalaVersion := "2.12.10"
  )

libraryDependencies += "log4j" % "log4j" % "1.2.14"
libraryDependencies += "org.apache.spark" %% "spark-core" % "2.4.0"
libraryDependencies += "org.apache.spark" %% "spark-mllib" % "2.4.0"
libraryDependencies += "com.github.fommil.netlib" % "all" % "1.1.2" pomOnly()
