export const imageDir = '../../../assets/images/home/';
import { AIModalCallback, LocalModalCallback, battleModalCallback, tournamentModalCallback, chatRoomModalCallback } from './callbacks.js';

// Array containing the objects for each element of the home-view that should be responsive
export const imageBook = [
    {
        id: 1,
        src: imageDir + 'card_ai.png',
        highleted: false,
        x: 65,
        y: 210,
        width: 160,
        height: 300,
        shadow: 5,
        lines: [0],
        callback: AIModalCallback,
    },
    {
        id: 2,
        src: imageDir + 'card_game.png',
        highleted: false,
        x: 250,
        y: 210,
        width: 160,
        height: 300,
        shadow: 5,
        lines: [1, 3],
        callback: battleModalCallback,
    },
    {
        id: 3,
        src: imageDir + 'card_thing.png',
        highleted: false,
        x: 450,
        y: 210,
        width: 160,
        height: 300,
        shadow: 5,
        lines: [2],
        callback: LocalModalCallback,
    },
    {
        id: 4,
        src: imageDir + 'card_chat.png',
        highleted: false,
        x: 900,
        y: 90,
        width: 260,
        height: 290,
        shadow: 5,
        lines: [11, 12, 15],
        callback: chatRoomModalCallback,
    },
    {
        id: 5,
        src: imageDir + 'card_tournament.png',
        highleted: false,
        x: 650,
        y: 210,
        width: 160,
        height: 300,
        shadow: 5,
        lines: [4, 5],
        callback: tournamentModalCallback,
    },
]

// Array containing the objects for each element of the home-view that should not be responsive
export const backgroundImageBook = [
    {
        // index: 0
        src: imageDir + 'polaroid_1.png', // alien kids
        x: 1350,
        y: 170,
        width: 100,
        height: 100,
        shadow: 3,
    },
    {
        // index: 1
        src: imageDir + 'polaroid_2.png', // big foot print
        x: 900,
        y: 500,
        width: 110,
        height: 110,
        shadow: 3,
    },
    {
        // index: 2
        src: imageDir + 'img_1.png', // lizard peeps newspaper
        x: 700,
        y: 620,
        width: 460,
        height: 260,
        shadow: 3,
    },
    {
        // index: 3
        src: imageDir + 'polaroid_3.png', // GWBush
        x: 1355,
        y: 370,
        width: 100,
        height: 100,
        shadow: 3,
    },
    {
        // index: 4
        src: imageDir + 'polaroid_4.png', // swamp monster
        x: 1370,
        y: 500,
        width: 100,
        height: 100,
        shadow: 3,
    },

    {
        // index: 5
        src: imageDir + 'polaroid_5.png', // big foot
        x: 210,
        y: 710,
        width: 130,
        height: 130,
        shadow: 3,
    },
    {
        // index: 6
        src: imageDir + 'polaroid_6.png', // power plant
        x: 450,
        y: 650,
        width: 90,
        height: 90,
        shadow: 3,
    },
    {
        // index: 7
        src: imageDir + 'polaroid_7.png', // toxic waste
        x: 520,
        y: 770,
        width: 110,
        height: 110,
        shadow: 3,
    },
    {
        // index: 8
        src: imageDir + 'img_3.png', // missing person
        x: 1680,
        y: 400,
        width: 200,
        height: 260,
        shadow: 3,
    },
    {
        // index: 9
        src: imageDir + 'img_4.png', // galactic map
        x: 1450,
        y: 650,
        width: 200,
        height: 200,
        shadow: 3,
    },
    {
        // index: 10
        src: imageDir + 'img_2.png', // area 51
        x: 1550,
        y: 100,
        width: 260,
        height: 260,
        shadow: 3,
    },
]

// Array containing the objects for the labels
export const labels = [
    {
        text: "gamePlay",
        x: 185,
        y: 80,
        width: 300,
        height: 50,
    },
    {
        text: "A.I.",
        x: imageBook[0].x,
        y: imageBook[0].y + imageBook[0].height + 15,
        width: imageBook[0].width,
        height: 50,
    },
    {
        text: "inviteFriends",
        x: imageBook[1].x,
        y: imageBook[1].y + imageBook[1].height + 15,
        width: imageBook[1].width,
        height: 50,
    },
    {
        text: "localGame",
        x: imageBook[2].x,
        y: imageBook[2].y + imageBook[2].height + 15,
        width: imageBook[2].width,
        height: 50,
    },
    {
        text: "chatRoom",
        x: imageBook[3].x,
        y: imageBook[3].y + imageBook[3].height + 15,
        width: imageBook[3].width,
        height: 50,
    },
    {
        text: "tournament",
        x: imageBook[4].x,
        y: imageBook[4].y + imageBook[4].height + 15,
        width: imageBook[4].width,
        height: 50,
    },
]

export const lines = [
    {
        //index: 0
        // Game Play to AI card
        x1: labels[0].x + (labels[0].width / 2),
        y1: labels[0].y + 40,
        x2: imageBook[0].x + (imageBook[0].width / 2),
        y2: imageBook[0].y + 10,
    },
    {
        //index: 1
        // Game Play to lizard people card
        x1: labels[0].x + (labels[0].width / 2),
        y1: labels[0].y + 40,
        x2: imageBook[1].x + (imageBook[1].width / 2),
        y2: imageBook[1].y + 10,
    },
    {
        //index: 2
        // Game Play to local card
        x1: labels[0].x + (labels[0].width / 2),
        y1: labels[0].y + 40,
        x2: imageBook[2].x + (imageBook[2].width / 2),
        y2: imageBook[2].y + 10,
    },
    {
        //index: 3
        // Lizard people card to Lizard people newspaper
        x1: imageBook[1].x + 70,
        y1: imageBook[1].y + 280,
        x2: backgroundImageBook[2].x + 20,
        y2: backgroundImageBook[2].y + 50,
    },
    {
        //index: 4
        // bigfoot card to bigfoot foot print polaroid
        x1: imageBook[4].x + 50,
        y1: imageBook[4].y + 290,
        x2: backgroundImageBook[1].x + 60,
        y2: backgroundImageBook[1].y + 10,
    },
    {
        //index: 5
        // bigfoot card to bigfoot polaroid
        x1: imageBook[4].x + 50,
        y1: imageBook[4].y + 290,
        x2: backgroundImageBook[5].x + 60,
        y2: backgroundImageBook[5].y + 20,
    },
    {
        //index: 6
        // bigfoot foot print polaroid  to bigfoot polaroid
        x1: backgroundImageBook[1].x + 60,
        y1: backgroundImageBook[1].y + 10,
        x2: backgroundImageBook[5].x + 60,
        y2: backgroundImageBook[5].y + 20,
    },
    {
        //index: 7
        // power plant polaroid  to toxic waste polaroid
        x1: backgroundImageBook[6].x + 60,
        y1: backgroundImageBook[6].y + 10,
        x2: backgroundImageBook[7].x + 60,
        y2: backgroundImageBook[7].y + 20,
    },
    {
        //index: 8
        // toxic waste polaroid to swamp monster polaroid
        x1: backgroundImageBook[7].x + 60,
        y1: backgroundImageBook[7].y + 20,
        x2: backgroundImageBook[4].x + 60,
        y2: backgroundImageBook[4].y + 10,
    },
    {
        //index: 9
        // swamp monster polaroid to missing person
        x1: backgroundImageBook[4].x + 60,
        y1: backgroundImageBook[4].y + 10,
        x2: backgroundImageBook[8].x + 90,
        y2: backgroundImageBook[8].y + 60,
    },
    {
        //index: 10
        // missing person to area 51 map
        x1: backgroundImageBook[8].x + 90,
        y1: backgroundImageBook[8].y + 60,
        x2: backgroundImageBook[10].x + 20,
        y2: backgroundImageBook[10].y + 180,
    },
    {
        //index: 11
        // area 51 map to chat room
        x1: backgroundImageBook[10].x + 20,
        y1: backgroundImageBook[10].y + 180,
        x2: imageBook[3].x + 110,
        y2: imageBook[3].y + 187,
    },
    {
        //index: 12
        // chat room to galactic map
        x1: imageBook[3].x + 110,
        y1: imageBook[3].y + 187,
        x2: backgroundImageBook[9].x + 20,
        y2: backgroundImageBook[9].y + 180,
    },
    {
        //index: 13
        // galactic map to area 51 map
        x2: backgroundImageBook[9].x + 20,
        y2: backgroundImageBook[9].y + 180,
        x1: backgroundImageBook[10].x + 20,
        y1: backgroundImageBook[10].y + 180,
    },
    {
        //index: 14
        // area 51 map to george w bush
        x1: backgroundImageBook[10].x + 20,
        y1: backgroundImageBook[10].y + 180,
        x2: backgroundImageBook[3].x + 45,
        y2: backgroundImageBook[3].y + 5,
    },
    {
        //index: 15
        // chat room to george w bush
        x1: imageBook[3].x + 110,
        y1: imageBook[3].y + 187,
        x2: backgroundImageBook[3].x + 45,
        y2: backgroundImageBook[3].y + 5,
    },
    {
        //index: 16
        // george w bush to alien kids polaroid
        x1: backgroundImageBook[3].x + 45,
        y1: backgroundImageBook[3].y + 5,
        x2: backgroundImageBook[0].x + 25,
        y2: backgroundImageBook[0].y + 90,
    },
    {
        //index: 17
        // george w bush to lizard people newspaper
        x1: backgroundImageBook[3].x + 45,
        y1: backgroundImageBook[3].y + 5,
        x2: backgroundImageBook[2].x + 20,
        y2: backgroundImageBook[2].y + 50,
    },
]