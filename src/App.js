'use client';
import { useState } from 'react';
import { AppBar, Toolbar, IconButton, Typography, Button, Box, Container } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import theme from "assets/theme";
import MKInput from "components/MKInput";
import MKButton from "components/MKButton"
import OverviewCard from 'components/overviewcard';
import CompetitorDetails from 'components/competitordetails';
import Skeleton from "@mui/material/Skeleton";
import logo from "logo"
import MKAvatar from "components/MKAvatar";

export default function Home() {
    const [inputValue, setInputValue] = useState('');
    const [response, setResponse] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        const apiRes = await fetch('/api/domain_info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ domain: inputValue }),
        });
        const data = await apiRes.json();
        setLoading(false);
        setResponse(data);
    };

    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <AppBar position="sticky" style={{ backgroundColor: '#6ad5e6' }}>
                <Container maxWidth="lg">
                    <Toolbar disableGutters>
                        <MKAvatar src={logo} alt="Logo" bgcolor='primary' style={{ width: '90px', height: '90px' }} variant="square"/>
                        <Box sx={{ display: { xs: 'none', md: 'block' } }}>
                            <MKButton variant="text" style={{ color: '#344767' }}> Home </MKButton>
                            <MKButton variant="text" style={{ color: '#344767' }}> Pricing </MKButton>
                            <MKButton variant="text" style={{ color: '#344767' }}> Contact </MKButton>
                        </Box>
                        <IconButton
                            style={{ color: '#344767' }}
                            aria-label="menu"
                            edge="end"
                            sx={{ display: { xs: 'block', md: 'none' } }}
                        >
                            <MenuIcon />
                        </IconButton>
                    </Toolbar>
                </Container>
            </AppBar>
            <Container maxWidth="md">
                <Box py={4} textAlign="center">
                    <Typography variant="h3" gutterBottom>
                        Domain Information Finder
                    </Typography>
                    <Typography variant="subtitle1" color="textSecondary" gutterBottom>
                        Enter a domain name to retrieve detailed information and competitor analysis.
                    </Typography>
                    <form onSubmit={handleSubmit} style={{ marginTop: '20px', display: 'flex', justifyContent: 'center' }}>
                        <MKInput
                            type="text"
                            label="Domain"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            required
                            style={{ width: '300px', marginRight: '10px' }}
                        />
                        <MKButton variant="gradient" type="submit" disabled={loading} style={{ backgroundColor: '#6ad5e6' }}>
                            <span style={{ color: '#344767' }}>
                            {loading ? 'Fetching...' : 'Fetch Info'}
                            </span>
                        </MKButton>
                    </form>
                </Box>
                
                {loading && (
                    <Box display="flex" flexDirection="column" alignItems="center" py={2}>
                        <Skeleton variant="rectangular" width="80%" height={120} />
                        <Skeleton variant="rectangular" width="80%" height={120} style={{ marginTop: '10px' }} />
                    </Box>
                )}
                {response && (
                    <>
                        <Typography variant="h4" gutterBottom>
                                Target Company Analysis
                        </Typography>
                        <OverviewCard overview={response.overview} />
                        <Box py={4}>
                            <Typography variant="h4" gutterBottom>
                                Competitor Analysis
                            </Typography>
                            {response.competitors.map((competitor) => (
                                <CompetitorDetails key={competitor.domain} competitor={competitor} />
                            ))}
                        </Box>
                    </>
                )}
            </Container>
        </ThemeProvider>
    );
}
