import { type OrbStatus } from '../types';
import './StatusOrb.css';

interface StatusOrbProps {
  status: OrbStatus;
  showInChat?: boolean;
}

const STATUS_LABELS: Record<OrbStatus, string> = {
  ready: 'Ready',
  processing: 'Processing',
  communicating: 'Communicating',
  error: 'Error',
};

export function StatusOrb({ status, showInChat = false }: StatusOrbProps) {
  return (
    <div className={`status-orb-container ${showInChat ? 'status-orb-container--in-chat' : ''}`}>
      <div className={`status-orb status-orb--${status}`}>
        <div className="orb-core"></div>
        <div className="orb-glow"></div>
        <div className="orb-pulse"></div>
      </div>
      {status !== 'ready' && (
        <div className="status-label-wrapper">
          <div className="status-label">{STATUS_LABELS[status]}</div>
        </div>
      )}
    </div>
  );
}
