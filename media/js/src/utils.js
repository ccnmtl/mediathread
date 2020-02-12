import Cookies from 'js-cookie';

/**
 * A wrapper for `fetch` that passes along auth credentials.
 */
const authedFetch = function(url, method = 'get', data = null) {
    const token = Cookies.get('csrftoken');
    return fetch(url, {
        method: method,
        headers: {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': token
        },
        body: data,
        credentials: 'same-origin'
    });
};

const getAssets = function(
    title='', owner='', tags=[], terms=[], date='all'
) {
    const params = new URLSearchParams();

    // Always include the annotations
    params.append('annotations', true);

    if (title) {
        params.append('search_text', title);
    }

    if (date !== 'all') {
        params.append('modified', date);
    }

    let basePath = '/api/asset/';
    if (owner && owner !== 'all') {
        basePath = `/api/asset/user/${owner}/`;
    }

    return authedFetch(basePath + '?' + params.toString())
        .then(function(response) {
            if (response.status === 200) {
                return response.json();
            } else {
                throw 'Error loading assets: ' +
                    `(${response.status}) ${response.statusText}`;
            }
        });
};

export {getAssets};
