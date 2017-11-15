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
  leafletOutput("map", width = "100%", height = "100%"),
  absolutePanel(id='controlPanel',
                top = 150, left = 10,
                fixed=T,
                draggable=T,
                sliderInput(
                  inputId="range",
                  label="Foo",
                  min=0,
                  max=100,
                  value=c(5,25),
                  step=5,
                  round=T
                ),
                sliderInput(
                  inputId="Month",
                  label="Month",
                  min=1,
                  max=12,
                  value=c(1,12),
                  step = 1,
                  round = T
                ),
                selectInput("Year", "Year", choices=c(2015,2016))
  )
))
