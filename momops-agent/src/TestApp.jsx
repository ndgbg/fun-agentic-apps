function TestApp() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>🤖 MomOps Test</h1>
      <p>If you can see this, the basic React app is working!</p>
      <div style={{ 
        background: 'linear-gradient(135deg, #A78BFA 0%, #F9A8D4 100%)',
        color: 'white',
        padding: '1rem',
        borderRadius: '8px',
        marginTop: '1rem'
      }}>
        ✅ React is working
        <br />
        ✅ CSS is working
        <br />
        🔄 Testing autonomous agent...
      </div>
    </div>
  )
}

export default TestApp