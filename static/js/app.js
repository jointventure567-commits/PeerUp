function togglePassword() {

    const password =
        document.getElementById("password");

    const button =
        document.querySelector(".password-toggle");


    if (!password) {
        return;
    }


    if (password.type === "password") {

        password.type = "text";

        button.textContent = "Hide";

    } else {

        password.type = "password";

        button.textContent = "Show";

    }

}



function searchMentors() {

    const input =
        document.getElementById("mentorSearch");

    if (!input) {
        return;
    }


    const search =
        input.value
            .toLowerCase()
            .trim();


    const mentorCards =
        document.querySelectorAll(".mentor-card");


    mentorCards.forEach(card => {

        const mentorData =
            card
                .getAttribute("data-name")
                .toLowerCase();


        if (
            mentorData.includes(search)
            || search === ""
        ) {

            card.style.display = "block";

        } else {

            card.style.display = "none";

        }

    });

}



document.addEventListener(
    "DOMContentLoaded",
    function () {

        const mentorSearch =
            document.getElementById("mentorSearch");


        if (mentorSearch) {

            mentorSearch.addEventListener(
                "keyup",
                function (event) {

                    if (event.key === "Enter") {

                        searchMentors();

                    }

                }
            );

        }

    }
);