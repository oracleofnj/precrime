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

# Define UI for application that draws a histogram
shinyUI(bootstrapPage(
  tags$style(type = "text/css", "html, body {width:100%;height:100%}"),
  leafletOutput("map", width = "100%", height = "100%"),
  absolutePanel(top = 10, right = 10,
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
