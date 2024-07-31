import React from 'react';
import { Accordion, AccordionDetails, AccordionSummary, Card, CardContent, Typography, Divider } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

function OverviewCard({ overview }) {
  return (
    <Card>
      <CardContent>
        <Typography>
          {overview.domain} Overview
	</Typography>
	<Divider sx={{ my: 2 }} />
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />} aria-controls="panel1a-content" id="panel1a-header">
            <Typography variant='h6'>Overview</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" color="text.secondary">
              <strong>{"Domain"}:</strong> {overview.domain}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>{"Description"}:</strong> {overview.description|| 'N/A'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>{"Global Rank"}:</strong> {overview.globalRank}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>{"Global Rank Change"}:</strong> {overview.globalRankChange}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>{"Country"}:</strong> {overview.country}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>{"Country Rank"}:</strong> {overview.countryRank}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>{"Total totalVisits"}:</strong> {overview.totalVisits}
            </Typography>
          </AccordionDetails>
        </Accordion>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />} aria-controls="panel1a-content" id="panel1a-header">
            <Typography variant='h6'>Employees</Typography>
          </AccordionSummary>
          <AccordionDetails>
            {Object.entries(overview.employees).length > 0 ? (
              Object.entries(overview.employees).map(([name, role]) => (
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
export default OverviewCard;
