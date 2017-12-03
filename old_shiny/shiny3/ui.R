#
# This is the user-interface definition of a Shiny web application. You can
# run the application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
# 
#    http://shiny.rstudio.com/
#

library("shiny")
library("shinydashboard")
library("highcharter")
library("dplyr")
library("viridisLite")
library("markdown")
library("quantmod")
library("tidyr")
library("DT")
library("shiny")
library("leaflet")
library("plotly")
library("wordcloud2")
library('scatterD3')


dashboardPage(
  skin = "black",
  dashboardHeader(title = "Crime Analysis", disable = FALSE),
  dashboardSidebar(
    sidebarMenu(
      menuItem("Map", tabName = "map", icon = icon("map-marker"))
    )
  ),
  dashboardBody(
    tags$head(tags$script(src = "js/ga.js")),
    tags$head(tags$link(rel = "stylesheet", type = "text/css", href = "css/custom_fixs.css")),
    tabItems(
      
      ################################################################################################ crime map
      tabItem(tabName = "map", 
              sidebarLayout(position = "right", 
                            sidebarPanel(
                              h4("Filter"),
                              
                              # widget for crime type
                              checkboxGroupInput("Crime_Type", label = "Crime_Type",
                                                 choices = c("BURGLARY", "FELONY ASSAULT", "GRAND LARCENY",
                                                             "GRAND LARCENY OF MOTOR VEHICLE", "RAPE", "ROBBERY",
                                                             "MURDER & NON-NEGL. MANSLAUGHTE"),
                                                 selected = c("BURGLARY", "FELONY ASSAULT", "GRAND LARCENY",
                                                              "GRAND LARCENY OF MOTOR VEHICLE", "RAPE","ROBBERY",
                                                              "MURDER & NON-NEGL. MANSLAUGHTE")),
                              
                              #date range
                              dateRangeInput("Date_Range", "Choose a date range", 
                                             start = "2016-10-01", end = "2016-12-31", 
                                             min = "2006-02-01", max = "2016-12-31"),
                              

                              
                              h4("Click the Update button to see the map: "),
                              #update button
                              actionButton("button", "Update", 
                                           style="color: #fff; background-color: #337ab7; border-color: #2e6da4")
                            ),
                            
                            mainPanel(
                              leafletOutput("map", width = "100%", height = 650)
                            )
              )
      )
    )
  )
)

