#
# This is the server logic of a Shiny web application. You can run the 
# application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
# 
#    http://shiny.rstudio.com/
#

library(shiny)
precincts <- geojsonio::geojson_read('nypd_precincts.geojson', what='sp')
bins <- c(2, 20, 50000, 70000, 100000, 120000, 140000, 180000, 250000)
pal <- colorBin(
  'viridis',
  domain=precincts$Population,
  bins=bins,
  reverse=T
)
highlight <- highlightOptions(
  weight = 5,
  color = "#666",
  dashArray = "",
  fillOpacity = 0.7,
  bringToFront = TRUE
)
labels <- sprintf(
  paste(
    "<strong>Precinct %d</strong><br/>",
    "Population: %s"
  ),
  as.integer(precincts$Precinct),
  format(as.integer(precincts$Population),big.mark=",", trim=TRUE)
) %>% lapply(htmltools::HTML)
labelopts <- labelOptions(
  style = list("font-weight" = "normal", padding = "3px 8px"),
  textsize = "15px",
  direction = "auto"
)
m <- leaflet(precincts) %>% setView(-74,40.7,11) %>% addTiles() %>% addPolygons(
  fillColor = ~pal(Population),
  weight=2,
  opacity=1,
  color='white',
  dashArray='3',
  fillOpacity = 0.7,
  highlight=highlight,
  label=labels,
  labelOptions = labelopts
)

shinyServer(function(input, output, session) {
   
  output$map <- renderLeaflet({
    m
  })
  
})
