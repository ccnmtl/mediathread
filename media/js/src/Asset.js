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

        // Use youtube's thumbnail format for getting the biggest
        // thumbnail available.
        if (
            this.asset.primary_type === 'youtube' &&
                this.asset.sources &&
                this.asset.sources.url
        ) {
            const youtubeId = getYouTubeID(this.asset.sources.url.url);
            return `https://img.youtube.com/vi/${youtubeId}/hqdefault.jpg`;
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
}
