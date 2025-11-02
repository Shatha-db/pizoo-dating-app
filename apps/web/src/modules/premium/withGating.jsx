import React, { useState, useEffect } from 'react';
import { getGatingState, resetDayIfNeeded } from './gating';
import UpsellModal from './UpsellModal';
import { useNavigate } from 'react-router-dom';

/**
 * Higher-Order Component to add gating logic to any component
 * @param {React.Component} Component - Component to wrap
 * @param {Object} options - Configuration options
 * @returns {React.Component} - Wrapped component with gating
 */
export default function withGating(Component, options = {}) {
  const { when = 'after', reason = 'daily_limit' } = options;

  return function GatedComponent(props) {
    const [upsellOpen, setUpsellOpen] = useState(false);
    const [gatingState, setGatingState] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
      // Reset day if needed on mount
      resetDayIfNeeded();
      // Get initial state
      setGatingState(getGatingState());
    }, []);

    const onGate = (customReason) => {
      setUpsellOpen(true);
      // Optional: track analytics
      console.log('Gating triggered:', customReason || reason);
    };

    const handleChoosePlan = (tier) => {
      setUpsellOpen(false);
      // Navigate to premium page or checkout
      navigate(`/premium?plan=${tier}`);
    };

    return (
      <>
        <Component
          {...props}
          gating={gatingState}
          onGate={onGate}
          updateGating={() => setGatingState(getGatingState())}
        />
        <UpsellModal
          open={upsellOpen}
          onClose={() => setUpsellOpen(false)}
          onChoose={handleChoosePlan}
          reason={reason}
        />
      </>
    );
  };
}
