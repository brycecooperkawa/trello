# [Web Application Development](https://gitlab.msu.edu/cse477-spring-2024/course-materials/): Final Exam

## Purpose

The purpose of this Final Exam is to assess your understanding of the essential elements of web application development covered this semester; these elements include: 

1. Reactive front-end design

2. Design of a data-driven backend

3. Session management

4. Asynchronous communication 

5. Web APIs

   

## Exam Format and Expectations

The exam is an asynchronous take-home exam that is worth 35% of the final course grade. Please note that: <u>like any class</u>, you are given more time to complete homework assignments than the exam; and, <u>like any class</u>, the purpose of the exam is to assess your independent problem-solving and understanding of the course material. It is against the spirit of our exam (<u>like any exam</u>) for us to offer students with implementation support, hints, or extensions. To be perfectly clear:

* The teaching team will **only** answer questions that seek to clarify an exam requirement.
* The teaching team **will not** help debug code, problem solve, or assist with deployment.

Like the homework assignments, your exam will be gradied using a rubric, which you will find at the bottom of this page. Like the homework assignments, the rubric components are "all or nothing". 

**Your exam application should be stand-alone** - that is, it should not be a part of your Homework 1 -3 implementation although you are welcome to use parts of your homework implementation to help you complete the exam requirements. 



## Exam Goals

The goal of the final exam is to develop a simplified version of the popular project management tool - [Trello]( https://trello.com/tour ).  Trello is a [Kanban](https://asana.com/resources/what-is-kanban) style application where progress of various project tasks can be easily understood by looking at visual representations. For example, a project can be visualized by a **Board**, different stages of the project are visualized by **Lists**, and **Cards** can be used within a List to represent various tasks. As the project progresses, Cards move from one List to another. For example, a Card for a task that has been completed can be moved from a *'Currently Doing'* List to *'Completed'* List by a team member. Your implementation will be a trimmed down version of a Kanban-style, list-making tool described in the specific requirements below. Before starting the exam, I strongly encourage you to make a free Trello account, and familiarize yourself with the basic functionality of the tool - it will make thr specific requirements below a lot easier to follow.



## Specific Requirements

 Your implementation must adhere to the following requirements:   

1.  **A Signup System:** You will develop pages that allow your users to first signup with an email and password and then use the same credentials to login. Only logged in users should be allowed to access the application interface. Users must have an ability to logout as well. Make sure that all stored passwords are encrypted in your database.
2.  **The Interface**: <br>
  **2.1. Sign-in properties:**  upon first sign in, users should be presented with a message to either open an existing Board, or create a new Board. If they choose to open an existing Board, you must provide a link to access each board they are a part of. If they choose to create a new Board, you must prompt them for (i) a *project name* and (ii) *a list of member emails* - the other users that are allowed to join the project. <br>
  **2.2. Board Properties:** Each Board is a web page that shows the *project name*, and three default Lists: (1) "To Do"  (2) "Doing" (3) and "Completed".<br>
  **2.3. List Properties**: Each List should display the list's name, and a set of Cards. When the project board is first created there will be no cards on any of the lists. Each list will have a button that allows Board members to add new Cards to that list.<br>
  **2.4. Card Properties**: Each Card must have a *text entry box*, and two buttons: Edit and Delete. The *text entry box*, is where a user can describe the details of the Card's task. The Edit button will enable the user to edit the content in the Card's *text entry box*; when editing is complete, the user should press the enter key to commit/save any content in the *text entry box* to the database. The Delete button should delete the card. <br>
  **2.5. Card Movement:** Users should be able to move Cards across the three default lists in a Board by clicking and dragging the cards from one list, to another.<br>
  **2.6. Live changes:**. When new Cards are created, or edits to existing cards are made by any user, all other logged-in users should see the updates live (without having to refresh or reload thier pages). Note that you should not allow users outside board members to see the Board, even if they are logged in. <br>  

3.  **Board Storage**:
  You need to store the state of each Board's Lists, (i.e. anything written inside it) in a persistent database for other team members to see when they are logged in. Once any user signs up and logins again, they should be presented with the projects they had created or are a part of. The Board page should always show the most up-to-date state. 
4.  **Chat System**: On each Board page, there will be a window option where a group member can chat  with other group members that are currently active and logged into the same Board page. Similar to HW 3, there will be two windows in the chat system: The first window will allow users to type in and submit their chat text, and the second window will display the text. 


## Submitting your assignment

Be sure to perform all development in the `Final-Exam` directory of your <u>Personal Course Repository</u> 



##### Submit Exam Code

1. Submit your assignment by navigating to the main directory of your <u>Personal Course Repository</u> and Pushing your repo to Gitlab; you can do this by running the following commands:

   ```bash
   git add .
   git commit -m 'submitting Final Exam'
   git push
   ```

2. You have now submitted the Final Exam; you can run the same commands to re-submit anytime before the deadline. Please check that your submission was successfully uploaded by navigating to the corresponding directory in Personal Course Repository online.



**Deploy your web application to Google Cloud**

Deploy your Dockerized App to Google Cloud by running the commands below from the Final Exam directory.

```bash
gcloud builds submit --tag gcr.io/cse477-spring-2024/exam
gcloud run deploy --image gcr.io/cse477-spring-2024/exam --platform managed
```

As we did in the homeworks, please retain the <u>Service URL</u>; You can visit the <u>Service URL</u> above to see a live version of your web application. 



##### Submit Final Exam Service URL (This is required):

[Submit the Service URL for your live web application in this Google Form](https://docs.google.com/forms/d/e/1FAIpQLSdovLsgArl0yyz53SE-k4l59sPz035fuNmAfCvT14w15nj1VQ/viewform). 



## Rubric

The exam is graded on a 100 point scale; all individual requirements recieve an "all or nothing" grade. The following guide will be used when grading your submission: 

**Specific Requirements:**

* <u> 10 points</u> -  The "Signup System" Requirements were met. 
* <u>10 points</u> -  The Interface "Sign-in Properties" Requirements were met.
* <u>10 points</u> -  The Interface "Board Properties" Requirements were met.
* <u>10 points</u> -  The Interface "List Properties" Requirements were met.
* <u>10 points</u> - The Interface "Card Properties" Requirements were met.
* <u>10 points</u> -  The Interface "Card Movement" Requirements were met.
* <u>10 points</u> - The Interface "Live Changes" Requirements were met.
* <u>10 points</u> -  The "Board Storage" requirements were met.
* <u>10 points:</u> The "Chat System" Requirements were met

**General Requirements:**

* <u>5 points</u> - Does the code adhere to Frontend best practices covered throughout the semester?
* <u>5 points</u> - Does the code adhere to Backend best practices covered throughout the semester?

**Please note that you will receive a 0 on the assignment if any of the following conditions are met:**

* Your containerized application does not compile
* Your application is non-functional
* Your submission was late
* Your work was plagiarized, borrowed, or copied
  * If this condition is met, you will also fail the course.
