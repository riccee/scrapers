'use client';
import JsonFormatter from 'react-json-formatter'
import { useState } from 'react';

export default function Home() {
  const [inputValue, setInputValue] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

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
    propertyStyle: { color: 'white' },
    stringStyle: { color: 'lightgreen' },
    numberStyle: { color: 'darkorange' }
  }

  return (
    <div style={{ padding: '20px' }}>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          required
          style={{ padding: '10px', marginRight: '10px' }}
        />
        <button type="submit" style={{ padding: '10px' }}>Submit</button>
      </form>
      {loading && <p>Loading...</p>}
      {response && < JsonFormatter json={response} tabWith={4} jsonStyle={jsonStyle} />}
    </div>
  );
}
 
