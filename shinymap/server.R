#
# This is the server logic of a Shiny web application. You can run the 
# application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
# 
#    http://shiny.rstudio.com/
#

library(shiny)
states <- geojsonio::geojson_read('/Users/jsamet/precrime/shinymap/us-states.json', what='sp')
bins <- c(0, 10, 20, 50, 100, 200, 500, 1000, Inf)
pal <- colorBin(
  'YlOrRd',
  domain=states$density,
  bins=bins
)
m <- leaflet(states) %>% setView(-96,37.8,4) %>% addTiles() %>% addPolygons(
  fillColor = ~pal(density),
  weight=2,
  opacity=1,
  color='white',
  dashArray='3',
  fillOpacity = 0.7
)

# Define server logic required to draw a histogram
shinyServer(function(input, output, session) {
   
  output$map <- renderLeaflet({
    m
  })
  
})
