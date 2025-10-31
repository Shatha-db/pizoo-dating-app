export default function Loader({ text = 'Loading...' }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      backgroundColor: '#fafafa'
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{
          width: '64px',
          height: '64px',
          margin: '0 auto 1rem',
          border: '4px solid #ec4899',
          borderTopColor: 'transparent',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}></div>
        <div style={{ color: '#6b7280', fontSize: '1rem' }}>
          {text}
        </div>
      </div>
    </div>
  );
}
