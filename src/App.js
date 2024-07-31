'use client';
import JsonFormatter from 'react-json-formatter'
import { useState, useEffect } from 'react';
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import theme from "assets/theme";
import MKInput from "components/MKInput";
import MKButton from "components/MKButton"
import { io } from 'socket.io-client';
import MKProgress from "components/MKProgress";



const socket = io('ws://localhost:5000/', {transports: ["websocket"]});


export default function Home() {
  const [inputValue, setInputValue] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    socket.on('progress', (progress) => {
      setProgress(progress);
    });

    return () => {
      socket.off('progress');
    };
  }, []);

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


  const jsonStyle = {
    propertyStyle: { color: 'black' },
    stringStyle: { color: 'black' },
    numberStyle: { color: 'darkorange' }
  }

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
        <MKButton variant = "gradient" color = "info" type="submit" style={{ padding: '10px' }}>Submit</MKButton>
      </form>
      {loading && <MKProgress value={progress} />}
      {response && < JsonFormatter json={response} tabWith={4} jsonStyle={jsonStyle} />}
    </div>
    </ThemeProvider>
  );
}

