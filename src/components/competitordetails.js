import React from 'react';
import { Accordion, AccordionDetails, AccordionSummary, Card, CardContent, Typography, Divider } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

function CompetitorDetails({ competitor }) {
  return (
    <Card>
      <CardContent>
        <Typography>
          {competitor.domain} Overview
  </Typography>
  <Divider sx={{ my: 2 }} />
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />} aria-controls="panel1a-content" id="panel1a-header">
            <Typography variant='h6'>Overview</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" color="text.secondary">
              <strong>{"Domain"}:</strong> {competitor.domain|| 'N/A'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>{"Description"}:</strong> {competitor.description|| 'N/A'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>{"Category"}:</strong> {competitor.categoryId || 'N/A'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>{"Category Rank"}:</strong> {competitor.categoryRank|| 'N/A'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>{"Total Visits"}:</strong> {competitor.totalVisits|| 'N/A'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>{"Similarity"}:</strong> {competitor.similarity|| 'N/A'}
            </Typography>
          </AccordionDetails>
        </Accordion>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />} aria-controls="panel1a-content" id="panel1a-header">
            <Typography variant='h6'>Employees</Typography>
          </AccordionSummary>
          <AccordionDetails>
            {Object.entries(competitor.employees).length > 0 ? (
              Object.entries(competitor.employees).map(([name, role]) => (
                <Typography key={name} variant="body2" color="text.secondary">
                  <strong>{name}:</strong> {role}
                </Typography>
              ))
            ) : (
              <Typography>No employee data available</Typography>
            )}
          </AccordionDetails>
        </Accordion>
      </CardContent>
    </Card>
  );
}
export default CompetitorDetails;
