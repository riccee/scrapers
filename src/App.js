
'use client';
import { useState, useEffect } from 'react';
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import theme from "assets/theme";
import MKInput from "components/MKInput";
import MKButton from "components/MKButton"
import MKProgress from "components/MKProgress";
import OverviewCard from 'components/overviewcard';
import CompetitorDetails from 'components/competitordetails';

export default function Home() {
    const [inputValue, setInputValue] = useState('');
    const [response, setResponse] = useState(null);
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);

    const handleSubmit = async(e) => {
        e.preventDefault();
        setLoading(true);
        const apiRes = await fetch('/api/domain_info', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        body: JSON.stringify({ domain: inputValue }),
    });
    console.log(apiRes);
    const data = await apiRes.json();
    setLoading(false);
    setResponse(data);
};

return (
   <ThemeProvider theme={theme}>
   <CssBaseline /> 
   <div style={{ padding: '20px' }}>
      <form onSubmit={handleSubmit} style={{ display: 'flex', alignItems: 'center' }}>
        <MKInput
          type="text"
	        label =  "Domain"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          required
          style={{ padding: '10px', marginRight: '10px' }}
        />
        <MKButton variant = "gradient" color = "info" type="submit" style={{ padding: '10px' }} disabled={loading}>{loading ? 'Submitting...' : 'Submit'}</MKButton>
      </form>
      {response && < OverviewCard overview={response.overview} />}
      {response && response.competitors.map((competitor) => (
        <CompetitorDetails key={competitor.domain} competitor={competitor} />
      ))}
    </div>
    </ThemeProvider>
  );
}

