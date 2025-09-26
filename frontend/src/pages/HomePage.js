import React from 'react';
import { Container, Typography, Paper, Box } from '@mui/material';

const HomePage = () => {
  return (
    <Container maxWidth="md">
      <Paper sx={{ my: 4, p: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Critical Infrastructure Vitals Index (CIVI)
        </Typography>
        <Typography variant="body1" paragraph>
          The Critical Infrastructure Vitals Index (CIVI) is a composite index that scores and ranks countries based on the health of their essential infrastructure. It provides a comprehensive snapshot of national capabilities across four critical pillars: Autonomy, Resilience, Sustainability, and Effectiveness.
        </Typography>

        <Box sx={{ my: 4 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            Why CIVI Matters
          </Typography>
          <Typography variant="body1" paragraph>
            In an interconnected world, the strength of a nation's critical infrastructure is a primary determinant of its economic stability, national security, and quality of life. CIVI provides a standardized framework for policymakers, researchers, and investors to:
          </Typography>
          <ul>
            <li><Typography>Benchmark national infrastructure performance.</Typography></li>
            <li><Typography>Identify strategic vulnerabilities and strengths.</Typography></li>
            <li><Typography>Guide policy and investment decisions.</Typography></li>
            <li><Typography>Promote global standards for infrastructure development.</Typography></li>
          </ul>
        </Box>

        <Box sx={{ my: 4 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            The Four Pillars
          </Typography>
          <Typography variant="body1" paragraph>
            CIVI evaluates infrastructure across four distinct dimensions:
          </Typography>
          <ol>
            <li><Typography><strong>Autonomy</strong>: A nation's ability to operate its critical systems without dependence on foreign entities.</Typography></li>
            <li><Typography><strong>Resilience</strong>: The capacity of infrastructure to withstand, adapt to, and recover from disruptions.</Typography></li>
            <li><Typography><strong>Sustainability</strong>: The environmental, social, and economic viability of infrastructure.</Typography></li>
            <li><Typography><strong>Effectiveness</strong>: The quality, accessibility, and performance of infrastructure services.</Typography></li>
                      </ol>
                  </Box>
          
                  <Box sx={{ my: 4 }}>
                    <Typography variant="h5" component="h2" gutterBottom>
                      Industries Covered
                    </Typography>
                    <Typography variant="body1" paragraph>
                      CIVI spans the following 11 critical industries:
                    </Typography>
                    <ul>
                      <li><Typography>Communications</Typography></li>
                      <li><Typography>Defence</Typography></li>
                      <li><Typography>Energy</Typography></li>
                      <li><Typography>Finance</Typography></li>
                      <li><Typography>Food & Agriculture</Typography></li>
                      <li><Typography>Healthcare</Typography></li>
                      <li><Typography>Transport</Typography></li>
                      <li><Typography>Water</Typography></li>
                      <li><Typography>Waste Management</Typography></li>
                      <li><Typography>Emergency Services</Typography></li>
                      <li><Typography>Information Technology</Typography></li>
                    </ul>
                  </Box>
          
                  <Box sx={{ my: 4 }}>
                    <Typography variant="h5" component="h2" gutterBottom>
                      Key Features
                    </Typography>
                    <Typography variant="body1" paragraph>
                      The CIVI application offers two main interactive pages:
                    </Typography>
                    <ul>
                      <li>
                        <Typography variant="h6" component="h3" gutterBottom>Explore Page</Typography>
                        <Typography variant="body1" paragraph>
                          The Explore page provides an interactive world map to visualize CIVI data. Users can hover over countries for scores, filter by industry and pillar, and see dynamic updates.
                        </Typography>
                      </li>
                      <li>
                        <Typography variant="h6" component="h3" gutterBottom>Analyse Page</Typography>
                        <Typography variant="body1" paragraph>
                          The Analyse page allows for deeper historical and comparative analysis. Users can compare multiple countries, industries, and pillars over time with customizable line colors and dynamic charting.
                        </Typography>
                      </li>
                    </ul>
                  </Box>
          
                  <Box sx={{ my: 4 }}>
                    <Typography variant="h5" component="h2" gutterBottom>
                      Methodology
                    </Typography>
                    <Typography variant="body1" paragraph>
                      The CIVI score is calculated through a multi-step process: Indicator Selection, Data Collection, Normalization (0-100 min-max scaling), Scoring, and Aggregation.
                    </Typography>
                  </Box>
                </Paper>
              </Container>
            );
          };
export default HomePage;
