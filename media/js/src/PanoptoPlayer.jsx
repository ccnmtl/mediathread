import React, {
    useEffect, useId, useRef, useState
} from 'react';
import PropTypes from 'prop-types';

export default function PanoptoPlayer({
    serverName,
    sessionId,
    videoParams = {
        interactivity: 'none',
        showtitle: 'false',
    },
    onReady,
    onStateChange,
    onError,
}) {
    const elementId = useId();

    const playerRef = useRef(null);

    const [status, setStatus] = useState('idle');

    useEffect(() => {
        async function setup() {
            if (!window.EmbedApi) {
                throw new Error('Panopto EmbedApi is unavailable.');
            }

            playerRef.current = new window.EmbedApi(elementId, {
                width: '100%',
                height: '100%',
                serverName,
                sessionId,
                videoParams,
                events: {
                    onReady: () => {
                        if (!playerRef.current) return;

                        setStatus('ready');

                        if (onReady) {
                            onReady(playerRef.current);
                        }
                    },

                    onStateChange: (state) => {
                        if (!playerRef.current) return;

                        if (onStateChange) {
                            onStateChange(state, playerRef.current);
                        }
                    },
                },
            });
        }

        setup();

        return () => {
            playerRef.current = null;
        };
    }, [
        elementId,
        serverName,
        sessionId,
    ]);

    return (
        <div data-panopto-status={status}>
            <div id={elementId} className='absolute inset-0 h-full w-full' />

            {status !== 'ready' && status !== 'error' && (
                <div>
                    Loading video...
                </div>
            )}
        </div>
    );
}

PanoptoPlayer.propTypes = {
    serverName: PropTypes.string.isRequired,
    sessionId: PropTypes.string.isRequired,
    videoParams: PropTypes.string,
    onReady: PropTypes.func,
    onStateChange: PropTypes.func,
    onError: PropTypes.func
};
