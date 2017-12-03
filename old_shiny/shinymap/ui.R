#
# This is the user-interface definition of a Shiny web application. You can
# run the application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
# 
#    http://shiny.rstudio.com/
#

library(shiny)
library(dplyr)
library(ggplot2)
library(leaflet)
library(geojsonio)

# Define UI for application that draws a histogram
shinyUI(bootstrapPage(
  tags$style(
    type = "text/css",
    "
    #controlPanel {
      border-style: solid;
      border-radius: 10px;
      border-color: #404040;
      background: rgba(127,127,127,0.5)
    }
    html, body {width:100%;height:100%}
    "
  ),
  leafletOutput("map", width = "100%", height = "100%")
))
