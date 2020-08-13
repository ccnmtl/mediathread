import isFinite from 'lodash/isFinite';
import find from 'lodash/find';
import findIndex from 'lodash/findIndex';
import {groupBy, sortBy} from 'lodash';

/**
 * A wrapper for `fetch` that passes along auth credentials.
 */
const authedFetch = function(url, method='get', data=null) {
    const elt = document.getElementById('csrf-token');
    const token = elt ? elt.getAttribute('content') : '';
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
    title='', owner='', tags=[], terms=[], date='all',
    offset=0, orderBy='title'
) {
    const params = new URLSearchParams();

    params.append('course', window.MediaThread.current_course);

    // Pagination
    params.append('limit', 20);
    params.append('offset', offset);

    // Ordering
    // https://django-tastypie.readthedocs.io/en/latest/resources.html#ordering
    params.append('order_by', orderBy);

    // Always include the annotations
    params.append('annotations', true);

    if (title) {
        params.append('search_text', title);
    }

    if (date !== 'all') {
        params.append('modified', date);
    }

    if (tags && tags.length > 0) {
        params.append('tag', tags.map(tag => tag.value));
    }

    if (terms && terms.length > 0) {
        terms.forEach(function(term) {
            params.append(`vocabulary-${term.data.vocab_id}`, term.data.id);
        });
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

/**
 * Get annotation metadata.
 */
const getAsset = function(id=null) {
    const courseId = window.MediaThread.current_course;

    let url = `/asset/?course=${courseId}`;

    if (id) {
        url = `/api/asset/${id}/?annotations=true&course=${courseId}`;
    }

    return authedFetch(url)
        .then(function(response) {
            if (response.status === 200) {
                return response.json();
            } else {
                throw 'Error loading asset: ' +
                    `(${response.status}) ${response.statusText}`;
            }
        });
};

const getAssetReferences = function(id=null) {
    let url = `/asset/references/${id}/`;

    return authedFetch(url)
        .then(function(response) {
            if (response.status === 200) {
                return response.json();
            } else {
                throw 'Error loading asset: ' +
                    `(${response.status}) ${response.statusText}`;
            }
        });
};

const createSelection = function(assetId, data) {
    return authedFetch(
        `/asset/create/${assetId}/annotations/`,
        'post',
        JSON.stringify(data)
    ).then(function(response) {
        if (response.status === 200) {
            return response.json();
        } else {
            throw 'Error making selection: ' +
                `(${response.status}) ${response.statusText}`;
        }
    });
};

const createSherdNote = function(assetId, data) {
    return authedFetch(
        `/asset/${assetId}/sherdnote/create/`,
        'post',
        JSON.stringify(data)
    ).then(function(response) {
        if (response.status === 201) {
            return response.json();
        } else {
            return response.json().then(json => {
                let errorText = '';

                for (let key in json) {
                    errorText += `${key}: ${json[key]}\n`;
                }
                errorText = errorText.slice(0, -1);

                throw errorText;
            });
        }
    });
};

const updateSherdNote = function(assetId, selectionId, data) {
    return authedFetch(
        `/asset/save/${assetId}/annotations/${selectionId}/`,
        'post',
        JSON.stringify(data)
    );
};

const deleteSelection = function(assetId, selectionId) {
    return authedFetch(
        `/asset/delete/${assetId}/annotations/${selectionId}/`,
        'post'
    ).then(function(response) {
        if (response.status === 200) {
            return response.json();
        } else {
            throw 'Error deleting selection: ' +
                `(${response.status}) ${response.statusText}`;
        }
    });
};

const getHours = function(totalSeconds) {
    return Math.floor(totalSeconds / 3600);
};

const getMinutes = function(totalSeconds) {
    const hours = Math.floor(totalSeconds / 3600);
    const seconds = totalSeconds - (hours * 3600);
    return Math.floor(seconds / 60);
};

const getSeconds = function(totalSeconds) {
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds - (hours * 3600)) / 60);
    const seconds = totalSeconds - (hours * 3600) - (minutes * 60);
    return Math.floor(seconds);
};

/**
 * Given a number of seconds as a float, return an array
 * containing [hours, minutes, seconds].
 */
const getSeparatedTimeUnits = function(totalSeconds) {
    return [
        getHours(totalSeconds),
        getMinutes(totalSeconds),
        getSeconds(totalSeconds)
    ];
};

/**
 * Parse a timecode string from HH:MM:SS or MM:SS string format into a
 * number. Unit is in seconds.
 */
const parseTimecode = function(str) {
    const parts = str.split(':');

    let col1 = null;
    let col2 = null;
    let col3 = null;

    if (parts.length > 2) {
        col1 = Number(parts[0]);
        col2 = Number(parts[1]);
        col3 = Number(parts[2]);
    } else {
        col2 = Number(parts[0]);
        col3 = Number(parts[1]);
    }

    if (isFinite(col1) && isFinite(col2) && isFinite(col3)) {
        return (col1 * 3600) + (col2 * 60) + col3;
    } else if (isFinite(col2) && isFinite(col3)) {
        return (col2 * 60) + col3;
    } else {
        return null;
    }
};

const pad2 = function(number) {
    return (number < 10 ? '0' : '') + number;
};

const formatTimecode = function(totalSeconds, requireHours=false) {
    const units = getSeparatedTimeUnits(totalSeconds);

    // Don't include hours if it's not necessary.
    if (!units[0] && !requireHours) {
        return pad2(units[1]) + ':' + pad2(units[2]);
    }

    return pad2(units[0]) + ':' + pad2(units[1]) + ':' + pad2(units[2]);
};

/**
 * Return a duration, given a selection's start and end time.
 */
const getDuration = function(start, end) {
    return Math.max(end - start, 0);
};

const capitalizeFirstLetter = function(str) {
    return str.length ?
        str.charAt(0).toUpperCase() + str.slice(1)
        : str;
};

/**
 * Display the day of an annotation object's modified time.
 * e.g. 05.08.2018
 *
 * Returns a string.
 */
const formatDay = function(obj) {
    const dateStr = obj.added;
    const date = new Date(Date.parse(dateStr));
    return date.toLocaleDateString(undefined, {
        month: '2-digit',
        day: '2-digit',
        year: 'numeric'
    }).replace(/\//g, '.');
};

/**
 * Get asset type.
 *
 * This corresponds to Asset.primary_labels in
 * mediathread/assetmgr/models.py
 */
const getAssetType = function(primaryType) {
    let type = primaryType;

    if (
        primaryType === 'youtube' ||
            primaryType === 'vimeo' ||
            primaryType === 'mp4_pseudo' ||
            primaryType === 'mp4_panopto' ||
            primaryType === 'quicktime' ||
            primaryType === 'video_pseudo'
    ) {
        type = 'video';
    } else if (primaryType === 'image_fpxid' || primaryType === 'image_fpx') {
        type = 'image';
    }

    return type;
};

const handleBrokenImage = function(assetType) {
    if (this) {
        // eslint-disable-next-line scanjs-rules/assign_to_src
        this.src = `/media/img/thumb_${assetType}.png`;
    }
};

/**
 * Given a react-player ref, return its current time.
 *
 * Returns a number, or a Promise on Vimeo videos.
 */
const getPlayerTime = function(internalPlayer) {
    const player = internalPlayer;
    if (player.getCurrentTime && typeof player.getCurrentTime === 'function') {
        return player.getCurrentTime();
    } else if (!isNaN(player.currentTime)) {
        return player.currentTime;
    }

    return null;
};

const getCourseUrl = function() {
    let courseUrl = '';
    if (window.MediaThread) {
        const courseId = window.MediaThread.current_course;
        courseUrl = `/course/${courseId}/`;
    }
    return courseUrl;
};

const getAssetUrl = function(assetId) {
    const courseUrl = getCourseUrl();
    return `${courseUrl}react/asset/${assetId}/`;
};

/**
 * Given an array of selections, return an object of those selections
 * grouped by author.
 */
const groupByAuthor = function(selections) {
    return sortBy(
        groupBy(selections, function(s) {
            return s.author.id;
        }), [
            function(group) {
                if (
                    group &&
                        group.length > 0 &&
                        group[0].author &&
                        group[0].author.public_name
                ) {
                    return group[0].author.public_name.toLowerCase();
                }

                return null;
            }
        ]);
};

/**
 * Given an array of selections, return an array of those selections
 * grouped by tag.
 *
 * Structure of returned array:
 *
 * [
 *   {
 *     tagName: 'tag name'
 *     tagId: 123
 *     selections: [ ... ]
 *   },
 *   ...
 * ]
 */
const groupByTag = function(selections) {
    const out = [];

    selections.forEach(function(s) {
        if (
            s.metadata && s.metadata.tags &&
                s.metadata.tags.length
        ) {
            s.metadata.tags.forEach(function(tag) {
                const foundTag = find(out, function(o) {
                    return parseInt(o.tagId, 10) === parseInt(tag.id, 10);
                });

                if (!foundTag) {
                    out.push({
                        tagName: getTagName(
                            tag.id, s, window.MediaThread.tag_cache),
                        tagId: tag.id,
                        selections: [s]
                    });
                } else {
                    foundTag.selections.push(s);
                }
            });
        } else {
            const foundTag = find(out, function(o) {
                return parseInt(o.tagId, 10) === 0;
            });
            if (!foundTag) {
                out.push({
                    tagName: 'No Tags',
                    tagId: 0,
                    selections: [s]
                });
            } else {
                foundTag.selections.push(s);
            }
        }
    });

    const sorted = sortBy(out, [
        function(group) {
            // Sort the 'No Tags' group to the end.
            if (group && group.tagId === 0) {
                return null;
            }

            if (group && group.tagName) {
                return group.tagName.toLowerCase();
            }

            return null;
        }
    ]);

    return sorted;
};

/**
 * Given a tag ID and a selection, return the tag name.
 */
const getTagName = function(tagId, selection, tagCache={}) {
    if (tagCache[tagId]) {
        return tagCache[tagId];
    }

    let tagName = 'No Tags';

    if (selection.metadata && selection.metadata.tags) {
        selection.metadata.tags.forEach(function(tag) {
            if (parseInt(tag.id, 10) === parseInt(tagId, 10)) {
                tagName = tag.name;
                tagCache[tagId] = tagName;
                return;
            }
        });
    }

    return tagName;
};

/**
 * Given an array of selection tags, return these in react-select's
 * format.
 */
const tagsToReactSelect = function(tags, isCreating=false) {
    if (!tags) {
        return [];
    }

    return tags.map(function(tag) {
        let label = `${tag.name} (${tag.count})`;
        if (isCreating) {
            label = tag.name;
        }

        return {
            value: tag.name,
            label: label
        };
    });
};

/**
 * Given an array of vocabularies, return these in react-select's
 * format.
 */
const termsToReactSelect = function(vocabs) {
    if (!vocabs) {
        return [];
    }

    return vocabs.map(function(term) {
        const termOptions = [];
        const termSet = term.term_set || term.terms;


        if (termSet) {
            termSet.forEach(function(t) {
                const data = t;
                data.vocab_id = term.id;

                termOptions.push({
                    label: `${t.display_name} (${t.count})`,
                    value: t.name,
                    data: data
                });
            });
        }

        return {
            value: term.name || term.display_name,
            label: term.name || term.display_name,
            options: termOptions
        };
    });
};

/**
 * Given an array of vocabularies, return just the terms.
 */
const termsToReactSelectValues = function(vocabs) {
    if (!vocabs) {
        return [];
    }

    const a = [];
    vocabs.forEach(function(term) {
        const termSet = term.term_set || term.terms;

        if (termSet) {
            termSet.forEach(function(t) {
                const data = t;
                data.vocab_id = term.id;

                a.push({
                    label: t.display_name || t.name,
                    value: t.name,
                    data: data
                });
            });
        }
    });

    return a;
};

/**
 * Open the selectionId selection in the given accordion, and make it
 * active.
 */
const openSelectionAccordionItem = function(
    $accordion, selectionId,
    scrollIntoView=false
) {
    $accordion.find('.collapse').each(function(idx, el) {
        const $el = jQuery(el);
        const sId = parseInt($el.data('selectionid'), 10);
        if (selectionId === sId) {
            $el.addClass('show');
            const $card = $el.closest('.card');
            $card.addClass('active');
            if (scrollIntoView) {
                $card[0].scrollIntoView();
            }
            return false;
        }
    });
};

/**
 * Given an array of assets and a new asset, put the new one in the
 * array. Return the new array.
 */
const updateAsset = function(assets, asset) {
    const newAssets = assets.slice(0);
    const idx = findIndex(newAssets, {id: asset.id});
    newAssets.splice(idx, 1, asset);
    return newAssets;
};

export {
    getAssets, getAsset, getAssetReferences,
    createSelection,
    createSherdNote, updateSherdNote,
    deleteSelection,
    getHours, getMinutes, getSeconds,
    pad2, getSeparatedTimeUnits, formatTimecode, parseTimecode,
    getDuration,
    capitalizeFirstLetter, formatDay, getAssetType,
    handleBrokenImage, getPlayerTime, getCourseUrl,
    getAssetUrl,
    groupByAuthor, groupByTag, getTagName,
    tagsToReactSelect, termsToReactSelect, termsToReactSelectValues,
    openSelectionAccordionItem,
    updateAsset
};
