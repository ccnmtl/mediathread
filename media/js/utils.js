/**
 * Random utility functions. Currently these are all related to
 * importing media.
 */

const isYouTubeURL = function(s) {
    const re = /^(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})(?:\S+)?$/;
    return s.match(re);
};

const isVimeoURL = function(s) {
    const re = /^(?:http|https)?:?\/?\/?(?:www\.)?(?:player\.)?vimeo\.com\/(?:channels\/(?:\w+\/)?|groups\/(?:[^\/]*)\/videos\/|video\/|)(\d+)(?:|\/\?)$/;
    return s.match(re);
};

const getVimeoIdFromUrl = function(url) {
    // Look for a string with 'vimeo', then whatever, then a
    // forward slash and a group of digits.
    const match = /vimeo.*\/(\d+)/i.exec(url);
    // If the match isn't null (i.e. it matched)
    if (match) {
        // The grouped/matched digits from the regex
        return match[1];
    }

    return null;
};

const isImgUrl = function(url) {
    const img = new Image();
    img.src = url;
    return new Promise((resolve) => {
        img.onerror = () => resolve(false);
        img.onload = () => resolve(true);
    });
};

const getMediaType = function(url) {
    if (isYouTubeURL(url)) {
        return 'youtube';
    } else if (isVimeoURL(url)) {
        return 'vimeo';
    }

    return isImgUrl(url).then(function(result) {
        if (result) {
            return 'image';
        }

        return null;
    });
};

/**
 * Refresh form display when import url changes.
 */
const refreshImportForm = function(urlInput, sourceUrl, mediaLabel='image') {
    if (mediaLabel === 'youtube') {
        const youtubeId = getYouTubeID(sourceUrl);
        sourceUrl = `https://i.ytimg.com/vi/${youtubeId}/hqdefault.jpg`;
    } else if (mediaLabel === 'vimeo') {
        const vimeoId = getVimeoIdFromUrl(sourceUrl);
        sourceUrl = `https://vumbnail.com/${vimeoId}.jpg`;
    }

    const submitButton = document.getElementById('import-submit-button');
    document.getElementById('import-form-label').value = mediaLabel;

    const thumbnailEl = document.getElementById('imported-thumbnail');
    thumbnailEl.style.display = 'none';
    submitButton.disabled = true;

    thumbnailEl.src = sourceUrl;
    jQuery(thumbnailEl).on('load', function() {
        thumbnailEl.style.display = 'block';
        jQuery(urlInput)
            .removeClass('is-invalid')
            .addClass('is-valid');
        submitButton.disabled = false;
    });

    jQuery(thumbnailEl).on('error', function() {
        thumbnailEl.style.display = 'none';
        jQuery(urlInput)
            .removeClass('is-valid')
            .addClass('is-invalid');
        submitButton.disabled = true;
    });

    const widthEl = document.getElementById('import-form-width');
    const heightEl = document.getElementById('import-form-height');
    widthEl.value = null;
    heightEl.value = null;

    // Don't read image dimensions if it's just a video thumbnail.
    if (mediaLabel === 'image') {
        jQuery(thumbnailEl).on('load', function() {
            widthEl.value = thumbnailEl.naturalWidth;
            heightEl.value = thumbnailEl.naturalHeight;
        });

    }
};

export {
    getMediaType, refreshImportForm
};
