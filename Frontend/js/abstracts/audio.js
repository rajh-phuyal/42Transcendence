import { translate } from '../locale/locale.js';
import $store from '../store/store.js';
import { $id } from './dollars.js';

export default class AudioPlayer {
    static instance = null;

    constructor() {
        if (AudioPlayer.instance) {
            return AudioPlayer.instance;
        }

        this.maxVolumeMusic = 0.2;
        this.maxVolumeSounds = 0.5;
        this.currentSong = null;
        this.playing = false;
        this.songs = [
            { title: "lobbyGame",            audio: new Audio("../assets/audio/music/lobby-game.mp3") },
            { title: "lobbyTournament",      audio: new Audio("../assets/audio/music/lobby-tournament.mp3") },
            { title: "chat",                 audio: new Audio("../assets/audio/music/chat.mp3") },
            { title: "home",                 audio: new Audio("../assets/audio/music/home.mp3") },
            { title: "profile",              audio: new Audio("../assets/audio/music/profile.mp3") },
            { title: "ufo",                  audio: new Audio("../assets/audio/music/ufo.mp3") },
            { title: "lizard-people",        audio: new Audio("../assets/audio/music/lizard-people.mp3") },
            { title: "snowman",              audio: new Audio("../assets/audio/music/snowman.mp3") },
            { title: "lochness",             audio: new Audio("../assets/audio/music/lochness.mp3") },
            { title: "404",                  audio: new Audio("../assets/audio/music/404.mp3") }
        ];

        this.sounds = [
            { name: "beep1",        audio: new Audio("../assets/audio/sounds/beep1.mp3") },
            { name: "beep2",        audio: new Audio("../assets/audio/sounds/beep2.mp3") },
            { name: "paddle",       audio: new Audio("../assets/audio/sounds/paddle.mp3") },
            { name: "powerup",      audio: new Audio("../assets/audio/sounds/powerup.mp3") },
            { name: "wall",         audio: new Audio("../assets/audio/sounds/wall.mp3") },
            { name: "gameover",     audio: new Audio("../assets/audio/sounds/gameover.mp3") },
            { name: "pause",        audio: new Audio("../assets/audio/sounds/pause.mp3") },
            { name: "unpause",      audio: new Audio("../assets/audio/sounds/unpause.mp3") },
            { name: "score",        audio: new Audio("../assets/audio/sounds/score.mp3") },
            { name: "toggle",       audio: new Audio("../assets/audio/sounds/toggle.mp3") },
            { name: "chat",         audio: new Audio("../assets/audio/sounds/chat.mp3") },
            { name: "chatToast",    audio: new Audio("../assets/audio/sounds/chat_toast.mp3") },
            { name: "toast",        audio: new Audio("../assets/audio/sounds/toast.mp3") },
            { name: "no",           audio: new Audio("../assets/audio/sounds/no.mp3") },
            { name: "click",        audio: new Audio("../assets/audio/sounds/click.mp3") }
        ];

        AudioPlayer.instance = this;
    }

    static getInstance() {
        if (!AudioPlayer.instance)
            AudioPlayer.instance = new AudioPlayer();
        return AudioPlayer.instance;
    }

    toggleMusic() {
        let newValue = $store.fromState('music');
        // Update the icon
        const iconElement = $id("nav-music");
        if (newValue) {
            iconElement.src     = window.origin + '/assets/icons_128x128/icon_music-on.png';
            iconElement.title   = translate("global:nav", "musicOn");
        } else {
            iconElement.src     = window.origin + '/assets/icons_128x128/icon_music-off.png';
            iconElement.title   = translate("global:nav", "musicOff");
        }
        // Play or stop the music
        this.playSound("toggle");
        if (!$store.fromState('music')) {
            this.stop();
        } else {
            if (this.currentSong)
                this.playMusic(this.currentSong.title);
        }
    }

    toggleSound() {
        let newValue = $store.fromState('sound');
        // Update the icon
        const iconElement = $id("nav-sound");
        if (newValue) {
            iconElement.src     = window.origin + '/assets/icons_128x128/icon_sound-on.png';
            iconElement.title   = translate("global:nav", "soundOn");
        } else {
            iconElement.src     = window.origin + '/assets/icons_128x128/icon_sound-off.png';
            iconElement.title   = translate("global:nav", "soundOff");
        }
        this.playSound("toggle");
    }

    playSound(name) {
        if (!$store.fromState('sound')) return;
        if (!name || name === "none") return;

        const sound = this.sounds.find(sound => sound.name === name);
        if (sound) {
            sound.audio.currentTime = 0;
            sound.audio.volume = this.maxVolumeSounds;
            sound.audio.loop = false;
            sound.audio.play();
        } else {
            console.log("Sound not found:", name);
        }
    }

    playMusic(title) {
        const newSong = this.songs.find(song => song.title === title);
        if (!newSong) {
            console.log("AudioManager: Song not found:", title);
            return;
        }

        // Make sure the song is looped
        newSong.audio.loop = true;
        // So that if the client turns it on later, the right song is played
        if (!$store.fromState('music')) {
            this.currentSong = newSong;
            return;
        }

        if (this.playing && this.currentSong === newSong)
            return;
        if (this.playing)
            this.crossfade(this.currentSong, newSong);
        else {
            this.playing = true;
            this.startFadeIn(newSong, 1000);
        }
    }

    crossfade(oldSong, newSong) {
        if (!$store.fromState('music')) return;
        this.startFadeOut(oldSong, 1000, () => {
            oldSong.audio.pause();
            oldSong.audio.currentTime = 0;
            oldSong.audio.volume = this.maxVolumeMusic;
        });
        this.startFadeIn(newSong, 1000);
    }

    startFadeOut(song, duration, callback) {
        const interval = 100;
        const steps = duration / interval;
        let step = 0;

        const fadeOut = setInterval(() => {
            if (step >= steps) {
                clearInterval(fadeOut);
                if (callback) callback();
            } else {
                song.audio.volume = Math.max(0, this.maxVolumeMusic * (1 - step / steps));
                step++;
            }
        }, interval);
    }

    startFadeIn(song, duration) {
        song.audio.volume = 0;
        song.audio.play();

        const interval = 100;
        const steps = duration / interval;
        let step = 0;

        const fadeIn = setInterval(() => {
            if (step >= steps) {
                clearInterval(fadeIn);
                song.audio.volume = this.maxVolumeMusic;
            } else {
                song.audio.volume = (step / steps) * this.maxVolumeMusic;
                step++;
            }
        }, interval);

        this.currentSong = song;
    }

    stop() {
        if (this.playing) {
            this.startFadeOut(this.currentSong, 1000, () => {
                this.currentSong.audio.pause();
                this.currentSong.audio.currentTime = 0;
                this.playing = false;
            });
        }
    }
}

// Create and export a single instance
const audioPlayer = AudioPlayer.getInstance();
export { audioPlayer };
