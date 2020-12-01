import getYouTubeID from 'get-youtube-id';
import {getAssetType} from './utils';

export default class Asset {
    constructor(data) {
        this.asset = data;
    }
    getType() {
        return getAssetType(this.asset.primary_type);
    }
    getThumbnail() {
        if (!this.asset) {
            return null;
        }
        const mediaPrefix = typeof MediaThread !== 'undefined' ?
            window.MediaThread.staticUrl : '/media/';
        // Use youtube's thumbnail format for getting the biggest
        // thumbnail available.

        if (
            this.asset.primary_type === 'youtube' &&
                this.asset.sources &&
                this.asset.sources.url
        ) {
            const proxyurl = 'https://cors-anywhere.herokuapp.com/';
            const youtubeId = getYouTubeID(this.asset.sources.url.url);
            const url = `https://img.youtube.com/vi/${youtubeId}/hqdefault.jpg`;
            return fetch(proxyurl + url)
                .then(response => response.status)
                .then(contents => {console.log(contents);
                    if(contents === 200){
                        return url;
                    } else {
                        return mediaPrefix + 'img/thumb_video.png';
                    }
                })
                .catch(() => console.log('Can’t access ' + url + ' response.'));
        } else if (
            this.asset.primary_type === 'vimeo' &&
                this.asset.sources &&
                this.asset.sources.vimeo
        ) {
            const vUrl = this.asset.sources.vimeo.url;
            const url = `https://vimeo.com/api/oembed.json?url=${vUrl}`;
            return fetch(url).then(function(response) {
                if (response.status === 200) {
                    return response.json().then(function(d) {
                        return d.thumbnail_url;
                    });
                } else {
                    return mediaPrefix + 'img/thumb_video.png';
                }
            });
        }

        return this.asset.thumb_url ||
            (
                (this.asset.sources &&
                 this.asset.sources.image) ?
                    this.asset.sources.image.url : null
            );

    }
    getImage() {
        if (!this.asset || !this.asset.sources) {
            return null;
        }
        const mediaPrefix = typeof MediaThread !== 'undefined' ?
            window.MediaThread.staticUrl : '/media/';
        if (!this.asset.sources.thumb){
            this.asset.sources.thumb = mediaPrefix + 'img/thumb_image.png';
        }
        return this.asset.sources.image ||
            this.asset.sources.thumb;
    }
    /**
     * extractSource
     *
     * Return an object containing this asset's source URL.
     * Taken from Juxtapose.
     */
    extractSource() {
        const o = this.asset.sources;
        if (o.youtube && o.youtube.url) {
            const youtubeID = getYouTubeID(o.youtube.url);
            return {
                url: `https://youtube.com/watch?v=${youtubeID}`,
                host: 'youtube'
            };
        }
        if (o.vimeo && o.vimeo.url) {
            return {
                url: o.vimeo.url,
                host: 'vimeo'
            };
        }
        if (o.video && o.video.url) {
            return {
                url: o.video.url
            };
        }
        if (o.mp4_pseudo && o.mp4_pseudo.url) {
            return {
                url: o.mp4_pseudo.url
            };
        }
        if (o.mp4_panopto && o.mp4_panopto.url) {
            return {
                url: o.mp4_panopto.url
            };
        }
        if (o.mp4_audio && o.mp4_audio.url) {
            return {
                url: o.mp4_audio.url
            };
        }
        if (o.image && o.image.url) {
            return {
                url: o.image.url,
                width: o.image.width,
                height: o.image.height
            };
        }
        return null;
    }
    getCaptionTrack() {
        if (!this.asset || !this.asset.metadata) {
            return null;
        }

        let key = this.asset.metadata.find(elt => elt.key === 'caption_track');
        return key ? key.value[0] : null;
    }
}
