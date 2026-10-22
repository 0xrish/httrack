function ready() {
    Level_no = 0;
    Book_no = 0;
    Lesson_no = 0;
    Lesson_name = "";
    levels = document.getElementsByClassName("lvls");
    assist = document.getElementsByClassName("assistance")[0];
    dialog = document.getElementsByClassName("dialog_box")[0];
    bookshelf = document.getElementsByClassName("bookshelf")[0];
    books = document.getElementsByClassName("s_cont");
    lessonshelf = document.getElementsByClassName("lessonshelf")[0];
    lessons = document.getElementsByClassName("lessons");
    level_book_thmb = Array.from(
        document.getElementsByClassName("lvl_bk_thmb")
    );
    lesson_contents = document.getElementsByClassName("lesson_contents")[0];
    lesson_type = document.getElementsByClassName("lssn_type");
    lesson_type_text = document.getElementsByClassName("lssn_type_txt");
    lesson_info_number = document.getElementsByClassName("lssn_no")[0];
    interactive_lesson = document.getElementsByClassName("int_lssn")[0];
    songs = document.getElementsByClassName("songs")[0];
    games = document.getElementsByClassName("games")[0];
    warmup = document.getElementsByClassName("warmup")[0];
    more = document.getElementsByClassName("more")[0];

    // STAGE 1: LEVEL CHOOSING
    Array.from(levels).forEach((lvl) => {
        lvl.addEventListener("click", () => {
            Array.from(levels).forEach((l) => {
                l.classList.remove("selected");
                l.classList.add("unselected");
            });
            lvl.classList.remove("unselected");
            Level_no = lvl.id;
            level_book_thmb.forEach((lbt) => {
                lbt.classList.remove("active");
            });
            // Assitance settings
            dialog.innerHTML = "Start with Book 1";
            //bookshelf settings
            Array.from(document.getElementsByClassName("bk_thmnls")).forEach(
                (b_thmb, thmb_ind) => {
                    b_thmb.src =
                        "Assets/Images/book_thumbnails/l" +
                        Level_no +
                        "b" +
                        (parseInt(thmb_ind) + 1) +
                        ".jpg";
                }
            );
            document.getElementsByClassName("bk_thmnls")[9].onload =
                function () {
                    bookshelf.classList.add("active");
                };

            //lessonshelf settings
            lessonshelf.classList.remove("active");
            lesson_contents.classList.remove("active");
            lesson_type[0].src = "";
            lesson_type_text[0].innerHTML = "";
            lesson_info_number.classList.remove("active");
            interactive_lesson.classList.remove("active");
            games.classList.remove("active");
            document
                .getElementsByClassName("lssn_info")[0]
                .classList.remove("active");
            if (Level_no == 1) {
                document.getElementsByClassName(
                    "shelf"
                )[0].style.backgroundColor = "rgb(255, 141, 19, 0.5)";
                document.getElementsByClassName(
                    "lessons"
                )[0].style.backgroundColor = "rgb(255, 141, 19, 0.5)";
            }
            if (Level_no == 2) {
                document.getElementsByClassName(
                    "shelf"
                )[0].style.backgroundColor = "rgb(199, 237, 199, 1)";
                document.getElementsByClassName(
                    "lessons"
                )[0].style.backgroundColor = "rgb(199, 237, 199, 1)";
            }
            if (Level_no == 3) {
                document.getElementsByClassName(
                    "shelf"
                )[0].style.backgroundColor = "lightblue";
                document.getElementsByClassName(
                    "lessons"
                )[0].style.backgroundColor = "lightblue";
            }
            Array.from(document.getElementsByClassName("bk_no_thmb")).forEach(
                (bkt) => {
                    bkt.classList.remove("active");
                }
            );

            // Remove the gamelist and gameinfo
            Array.from(document.getElementsByClassName("gamelist")).forEach(
                (gl) => {
                    gl.remove();
                }
            );
            Array.from(document.getElementsByClassName("game_info")).forEach(
                (gi) => {
                    gi.remove();
                }
            );
        });
    });

    // STAGE 2: BOOK CHOOSING
    Array.from(books).forEach((bks) => {
        bks.addEventListener("click", () => {
            lesson_contents.classList.remove("active");
            levels[parseInt(Level_no) - 1].classList.add("selected");
            Book_no = bks.id;
            bookshelf.classList.remove("active");
            lessonshelf.classList.add("active");
            level_book_thmb.forEach((lbt) => {
                lbt.classList.remove("active");
            });
            level_book_thmb[parseInt(Level_no) - 1].src =
                "Assets/Images/book_thumbnails/l" +
                Level_no +
                "b" +
                parseInt(Book_no) +
                ".jpg";
            level_book_thmb[parseInt(Level_no) - 1].classList.add("active");
            dialog.innerHTML = "Book " + Book_no;
            lesson_type[0].src = "";
            lesson_type_text[0].innerHTML = "";
            lesson_info_number.classList.remove("active");
            document
                .getElementsByClassName("lssn_info")[0]
                .classList.remove("active");
            document.getElementsByClassName("bk_no_thmb")[
                parseInt(Level_no) - 1
            ].innerHTML = "Book " + Book_no;
            document
                .getElementsByClassName("bk_no_thmb")
                [parseInt(Level_no) - 1].classList.add("active");

            // Remove the gamelist and gameinfo
            Array.from(document.getElementsByClassName("gamelist")).forEach(
                (gl) => {
                    gl.remove();
                }
            );
            Array.from(document.getElementsByClassName("game_info")).forEach(
                (gi) => {
                    gi.remove();
                }
            );
        });
    });
    // STAGE 3: LESSON CHOOSING
    var newScript;
    Array.from(document.getElementsByClassName("lssn")).forEach(
        (lssn, lssn_ind) => {
            lssn.addEventListener("click", () => {
                Lesson_no = parseInt(lssn_ind) + 1;
                lessonshelf.classList.remove("active");
                lesson_contents.classList.add("active");
                if (Level_no == 1) {
                    document.getElementsByClassName("lssn_info")[0].style.left =
                        "34vw";
                }
                if (Level_no == 2) {
                    document.getElementsByClassName("lssn_info")[0].style.left =
                        "61vw";
                }
                if (Level_no == 3) {
                    document.getElementsByClassName("lssn_info")[0].style.left =
                        "84vw";
                }
                document
                    .getElementsByClassName("lssn_info")[0]
                    .classList.add("active");
                Array.from(document.getElementsByClassName("l_b_ls")).forEach(
                    (lbls) => {
                        lbls.innerText =
                            "L" +
                            Level_no +
                            "-B" +
                            Book_no +
                            "-Lesson " +
                            Lesson_no;
                    }
                );
                lesson_type[0].src = "";
                lesson_type_text[0].innerHTML = "";
                if ([1, 6, 11, 16].includes(parseInt(Lesson_no))) {
                    lesson_type[0].src = "Assets/Images/vocab.png";
                    lesson_type_text[0].innerHTML = "Topic Vocabulary";
                }
                if ([2, 7, 12, 17].includes(parseInt(Lesson_no))) {
                    lesson_type[0].src = "Assets/Images/abc.png";
                    lesson_type_text[0].innerHTML = "ABC friends";
                }
                if ([3, 8, 13, 18].includes(parseInt(Lesson_no))) {
                    lesson_type[0].src = "Assets/Images/cheesy.png";
                    lesson_type_text[0].innerHTML = "Cheesy stories";
                }
                if ([4, 9, 14, 19].includes(parseInt(Lesson_no))) {
                    lesson_type[0].src = "Assets/Images/math.png";
                    lesson_type_text[0].innerHTML = "Math";
                }
                if ([5, 10, 15, 20].includes(parseInt(Lesson_no))) {
                    lesson_type[0].src = "Assets/Images/bear.png";
                    lesson_type_text[0].innerHTML = "Bear and mouse";
                }
                lesson_info_number.classList.add("active");
                lesson_info_number.innerHTML = "Lesson " + Lesson_no;
                dialog.innerHTML = "Book " + Book_no + " Lesson " + Lesson_no;

                document.getElementsByClassName("studentbook")[0].src = "";
                document.getElementsByClassName("workbook")[0].src = "";
                document.getElementsByClassName("sbook_info")[0].innerHTML = "";
                document.getElementsByClassName("wbook_info")[0].innerHTML = "";
                interactive_lesson.classList.remove("active");

                Array.from(document.getElementsByTagName("script")).forEach(
                    (scpt) => {
                        if (scpt.parentNode == "head") {
                            document
                                .getElementsByTagName("head")[0]
                                .removeChild(scpt);
                        }
                    }
                );
                newScript = document.createElement("script");
                newScript.type = "text/javascript";
                newScript.src =
                    "Assets/JavaScript/l" +
                    Level_no +
                    "b" +
                    Book_no +
                    "l" +
                    Lesson_no +
                    ".js";
                document.getElementsByTagName("head")[0].appendChild(newScript);
                // lssn.style.backgroundColor = "rgb(250, 107, 89, 0.4)";

                // Make ready for next stage, fast loading, no delay in ppt thumbnail display
                newScript.onload = () => {
                    document.getElementsByClassName("studentbook")[0].src =
                        "Assets/Images/" +
                        content_informations.lesson +
                        "/thumbnails/Slide1.jpeg";
                    document.getElementsByClassName("workbook")[0].src =
                        "Assets/Images/" +
                        content_informations.worksheet +
                        "/thumbnails/Slide1.jpeg";
                    document.getElementsByClassName("sbook_info")[0].innerHTML =
                        "Student Book <br /> " +
                        lesson_type_text[0].innerHTML +
                        "<br />Page " +
                        content_informations.lesson.split("p")[1];
                    document.getElementsByClassName("wbook_info")[0].innerHTML =
                        "Work Book <br /> " +
                        lesson_type_text[0].innerHTML +
                        "<br />Page " +
                        content_informations.worksheet.split("p")[1];

                    // Remove the gamelist and gameinfo
                    Array.from(
                        document.getElementsByClassName("gamelist")
                    ).forEach((gl) => {
                        gl.remove();
                    });
                    Array.from(
                        document.getElementsByClassName("game_info")
                    ).forEach((gi) => {
                        gi.remove();
                    });
                    // load contents for game tab
                    if (content_informations.game != undefined) {
                        var gamelist = content_informations.game.split(",");
                        for (var gl = 0; gl < gamelist.length; gl++) {
                            let newImage = document.createElement("img");

                            newImage.setAttribute("class", "gamelist");
                            newImage.setAttribute(
                                "id",
                                gamelist[gl].replace(/\s+/g, "")
                            );
                            newImage.src =
                                "Assets/Images/game_thumbnails/g" +
                                gamelist[gl].match(/\d+/g)[0] +
                                "b" +
                                gamelist[gl].match(/\d+/g)[2] +
                                ".png";

                            let newp = document.createElement("p");
                            newp.setAttribute("class", "game_info");
                            console.log(gamelist[gl]);
                            switch (gamelist[gl].match(/\d+/g)[0]) {
                                case "1":
                                    var gamename = "Make a match";
                                    break;
                                case "2":
                                    var gamename = "Double trouble";
                                    break;
                                case "3":
                                    var gamename = "Memory";
                                    break;
                                case "4":
                                    var gamename = "Give me five";
                                    break;
                                case "7":
                                    var gamename = "Name that sound";
                                    break;
                                default:
                                    var gamename = "Game";
                                    break;
                            }
                            newp.innerHTML = gamename;

                            newImage.addEventListener("click", () => {
                                // localStorage.setItem("a", newImage.id);

                                // window.open(
                                //     "https://bigbeargameslibrary.netlify.app/Html/" +
                                //         newImage.id +
                                //         ".html",
                                //     "_blank"
                                // );

                                win = window.open();
                                win.document.body.style.margin = "0";
                                win.document.body.style.height = "100vh";
                                var iframe =
                                    win.document.createElement("iframe");
                                iframe.style.border = "none";
                                iframe.style.width = "100%";
                                iframe.style.height = "100%";
                                iframe.style.margin = "0";
                                if (newImage.id.match(/\d+/g)[0] < 6) {
                                    iframe.src =
                                        "https://bigbeargameslibrary1.netlify.app/Html/" +
                                        newImage.id +
                                        ".html";
                                } else {
                                    iframe.src =
                                        "https://bigbeargameslibrary2.netlify.app/Html/" +
                                        newImage.id +
                                        ".html";
                                }
                                win.document.body.appendChild(iframe);
                            });
                            document
                                .querySelectorAll(".games .ppts")[0]
                                .append(newImage, newp);
                        }
                    }
                };
            });
        }
    );
    lesson_info_number.addEventListener("click", () => {
        document
            .getElementsByClassName("lssn_info")[0]
            .classList.remove("active");
        lesson_contents.classList.remove("active");
        lessonshelf.classList.add("active");
        document.getElementsByClassName("studentbook")[0].src = "";
        document.getElementsByClassName("workbook")[0].src = "";
        document.getElementsByClassName("sbook_info")[0].innerHTML = "";
        document.getElementsByClassName("wbook_info")[0].innerHTML = "";
        interactive_lesson.classList.remove("active");

        dialog.innerHTML = "Book " + Book_no;
    });

    // STAGE 4: PPT/ VIDEO DISPLAY
    interactive_lesson.addEventListener("click", () => {
        // document.getElementsByClassName("studentbook")[0].src = "Assets/Images/" + content_informations.lesson + "/thumbnails/Slide1.jpeg";
        // document.getElementsByClassName("workbook")[0].src = "Assets/Images/" + content_informations.worksheet + "/thumbnails/Slide1.jpeg";
        // document.getElementsByClassName("sbook_info")[0].innerHTML = "Student Book <br /> " + lesson_type_text[0].innerHTML + "<br />Page " + content_informations.lesson.split('p')[1];
        // document.getElementsByClassName("wbook_info")[0].innerHTML = "Work Book <br /> " + lesson_type_text[0].innerHTML + "<br />Page " + content_informations.worksheet.split('p')[1];
        // // console.log(content_informations.lesson)
        interactive_lesson.classList.add("active");
        games.classList.remove("active");
    });

    document
        .getElementsByClassName("studentbook")[0]
        .addEventListener("click", () => {
            var ppt =
                "l" +
                Level_no +
                "b" +
                Book_no +
                "p" +
                content_informations.lesson.split("p")[1];
            localStorage.setItem("a", ppt);
            // location.href =  "Assets/Html/" + ppt + ".html";
            window.open("Assets/Html/" + ppt + ".html", "_blank");
        });
    document
        .getElementsByClassName("workbook")[0]
        .addEventListener("click", () => {
            var ppt =
                "l" +
                Level_no +
                "b" +
                Book_no +
                "p" +
                content_informations.worksheet.split("p")[1];
            localStorage.setItem("a", ppt);
            // location.href =  "Assets/Html/" + ppt + ".html";
            window.open("Assets/Html/" + ppt + ".html", "_blank");
        });
    songs.addEventListener("click", () => {
        interactive_lesson.classList.remove("active");
        games.classList.remove("active");
    });
    games.addEventListener("click", () => {
        interactive_lesson.classList.remove("active");
        games.classList.add("active");
    });
    warmup.addEventListener("click", () => {
        interactive_lesson.classList.remove("active");
        games.classList.remove("active");
    });
    more.addEventListener("click", () => {
        interactive_lesson.classList.remove("active");
        games.classList.remove("active");
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ready());
} else {
    ready();
}
