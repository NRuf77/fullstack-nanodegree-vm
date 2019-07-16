# Catalog app project submission for Udacity course "full stack web developer"

Catalog app written by Nikolaus Ruf as part of the requirements for passing the
course.

This repository was forked from the Udacity repository containing the virtual
machine configuration for the "full stack web developer" course.
The original README.md content can be found below for reference.

The application code submitted for the second project "catalog app" has been
added in subdirectory 'vagrant/catalog'.

## Starting the catalog app

To run the catalog app, follow these steps:

 1. Download and install Vagrant from
    [www.vagrantup.com](https://www.vagrantup.com/downloads.html).
    
 2. Download and install VirtualBox from
    [www.virtualbox.org](https://www.virtualbox.org/wiki/Downloads).
    
 3. On Windows, make sure that virtualization is enabled in BIOS.
 
 4. Start a Linux shell to run vagrant. On Windows, you can use the Git Bash
    shell that comes with [Git for Windows](https://git-scm.com/downloads).
    
 5. In the shell, switch to the *vagrant* subdirectory from the VM configuration
    and run the command
    ```
    $ vagrant up
    ```
    This can take a while to complete the first time you run it since a lot of
    data will be downloaded from the internet.
    
 6. To log into the VM, use
    ```
    $ vagrant ssh
    ```
    
 7. Install additional Python packages
    ```
    $ sudo pip install sqlalchemy
    $ sudo pip install requests
    $ sudo pip install bleach
    ```
    
 8. Switch to the app directory
    ```
    $ cd /vagrant/catalog
    ```
    
 9. Create an empty database in /vagrant/catalog/data via
    ```
    $ python scripts/db_setup.py
    ```
    
10. *Optional:* to pre-fill the catalog with a few (silly) categories and
    items, run
    ```
    $ python scripts/db_fill.py
    ```
    The app also works if the database is empty.
    
11. Obtain a client secret file from the Google developer portal (instructions
    below), rename it to client_secret.json and put it into
    /vagrant/catalog/data.
    
12. From /vagrant/catalog, start the app via
    ```
    $ python start_script.py
    ```
    The app writes some log messages to the console and a file catalog.log.
    Apart from the Flask app status, the log contains information on failed
    database requests and the progress of the sign in procedure.
    
13. Open a web browser on your own machine and go to http://localhost:5000

## Google OAuth2 client secret

To use Google's OAuth2 service for authentication, the app needs a JSON file
with client information from Google:

 1. Go to the [Google developer page](https://console.developers.google.com/)
    and sign up for a new / sign in with an existing Google account.
    
 2. Create a new application using the menu at the top.
 
 3. Choose 'Create credentials' as suggested by Google and select OAuth client
    ID.
    
 4. Google will ask you to configure the consent screen first, where you must
    provide at least an application name. Click save to proceed.
    
 5. Now choose "Web application" for the type of credentials.
 
 6. Give the client a name, enter
 
    > http://localhost:5000
    
    as authorized Javascript origin, and enter
    
    > http://localhost
    
    as authorized redirect URI. While the
    [Google docs](https://developers.google.com/identity/sign-in/web/server-side-flow)
    claim that no redirect URI is required for the kind of authentication used
    by the app, the function
    oauth2client.client.credentials_from_clientsecrets_and_code() will raise an
    exception if no URI is configured.
 
 7. Click on create and return to the main page. Then select the newly created
    credentials again and download a JSON file with client secret and other
    information using the menu at the top. 

## App functions and layout

The app serves both HTML pages and JSON objects.

All HTML pages have a sign in/sign out button in the upper right corner.
Clicking on sign in opens a pop-up for the Google OAuth2 sign in service.
If sign in is successful, the current page is reloaded and may now offer add,
edit, or delete functions to the user as appropriate.
Sign-out redirects to the main page and revokes any ability to add, edit, or
delete content.

The following HTML pages are available by path:

* **/:** main page showing the list of categories on the left and the 10 most
  recently added items on the right. If the user is signed in, there are also
  buttons to add an item or category in the menu on the left. Clicking on a
  category or item name links to the description of that object.
  
* **/category/view/[ID]:** for a valid integer ID, displays the category
  information with associated items. There is a button to go back to the main
  page in the menu on the left. If the user is signed in and is also the
  creator of the category, the menu shows buttons to edit or delete the
  category and to add an item. Clicking on an item links to its description.
  
* **/category/add:** the user needs to be signed in to see this page. There is
  a form to enter the category name with a submit button. The menu on the left
  also has buttons for going back to the main page or the category page.
  
* **/category/edit/[ID]:** for a valid integer ID, displays the category edit
  page. The user needs to be signed in and be the creator of the category to
  edit it. The layout is the same as for /category/add except that the name is
  pre-filled.
  
* **/category/delete/[ID]:** as /category/edit except that the name in the form
  is non-editable and submitting the form deletes the category.
  
* **/item/view/[ID]:** for a valid integer ID, displays the item information
  (name, category, description). There are buttons to go to the main page or
  the category page in the menu on the left. If the user is signed in and is
  also the creator of the item, the menu shows buttons to edit or delete the
  item.
  
* **/item/add/ or /item/add/[ID]:** the user needs to be signed in and have
  created at least one category to see this page. If the ID for a category
  belonging to the user is provided, the corresponding category is pre-selected
  in the drop-down menu for categories. Otherwise, the first category is
  selected. The page contains a form to select a category and enter a name and
  description for a new item. The menu on the left contains buttons linking
  back to the main page, category page, and item page.
  
* **/item/edit/[ID]:** for a valid integer item ID, displays the item edit page.
  The user needs to be signed in and be the creator of the item to edit it. The
  layout is the same as for /item/add except that all form elements are
  pre-filled.
  
* **/item/delete/[ID]:** as /item/edit except that the form elements are
  non-editable and submitting the form deletes the item.

Attempting to access a page for a non-existing ID or with insufficient
authorization returns the user to the main page and displays an appropriate
flash message.

These endpoints do not serve a HTML page but JSON objects:

* **/json/categories:** returns a JSON object using as keys the integer
  IDs and as values the names of all categories
  
* **/json/latest_items/[NUM]:** returns a JSON object using as keys the integer
  IDs of the latest NUM items and as values JSON objects with item information
  (name, category ID, category name)
  
* **/json/category/[ID]:** returns a JSON object with information for the
  category with the given ID (ID, name, and a list of items; the latter is a 
  SON object using as keys the integer item IDs and as values the item names)
  
* **/json/item/[ID]:** returns a JSON object with information for the item with
  the given ID (ID, name, description, category ID, category name)

Trying to obtain data for a non-existent ID yields a 404 NOT FOUND response.

## Project structure

The source code and application data are distributed among the following
subdirectories:

* **catalog:** the Python source code; see below

* **data:** the database and client secrets file which need to be created
  during setup; the git repository only contains a dummy file that enables
  committing the directory
  
* **scripts:** Python scripts for creating, filling, and testing the database

* **static:** CSS style file for HTML pages

* **templates:** Jinja2 templates for HTML pages, see below

### Python source code

The catalog subdirectory contains an __init__.py file so Python treats it as a
module.

The catalog app functionality is split into three parts:

* **app.py:** the Flask app handles authentication and control flow for
  requests; it uses a content manager defined in content.py to obtain content
  
* **content.py:** the content manager is responsible for retrieving data from
  the database manager and filling in templates
  
* **database.py:** the database manager wraps a sqlite3 database via sqlalchemy
  and provides access functions that serve content in the format required by
  the content manager

The start script for the app is start_script.py in the main directory.
All configuration information (paths, ports, etc.) is managed in that script.

### HTML templates

The templates subdirectory contains Jinja2 templates for HTML pages.
All pages extend base.html which contains the header information, basic page
layout, and Javascript components for accessing the Google OAuth2 service.
The other files are named like the page they belong to, e.g., main.html,
category_view.html, etc.

### Data model

The catalog app uses a sqlite3 database to store user, category, and item
information. Only the database manager defined in database.py accesses the
database directly.

The following tables are defined using sqlalchemy ORM functionality:

1. **table users:** tracks registered users
   * **column id (integer):** internal user ID, primary key
   * **column aut_id (string):** Google ID provided by OAuth2 service, must be
   unique
   
   The Google user name is not stored since it may change for a given user ID. 
   It is instead taken from the user data provided by Google when signing in.

2. **table categories:** tracks catalog categories
   * **column id (integer):** internal category ID, primary key
   * **name (string):** category name, must be unique
   * **user_id (integer):** user ID of creator / owner, foreign key referencing
     table users
     
   Only the original owner can edit a category, delete a category, or add items
   to it.

3. **table items:** tracks catalog items
   * **id (integer):** internal item ID, primary key
   * **name (string):** item name, must be unique
   * **description (string):** item description
   * **created (datetime):** item creation (not edit) date
   * **category_id:** ID of category item belongs to, foreign key referencing
     table categories
   * **user_id:** user ID of creator / owner, foreign key referencing table
     users
   
   Only the original owner can edit or delete an item.

---
(original README.md)

# Full Stack Web Developer Nanodegree program virtual machine

<a href="https://www.udacity.com/">
  <img src="https://s3-us-west-1.amazonaws.com/udacity-content/rebrand/svg/logo.min.svg" width="300" alt="Udacity logo">
</a>

Virtual machine for the [Relational Databases](https://www.udacity.com/course/intro-to-relational-databases--ud197) and [Full Stack Foundations](https://www.udacity.com/course/full-stack-foundations--ud088) courses in the [Full Stack Web Developer Nanodegree program](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Intro](#intro)
- [Installation](#installation)
- [Instructions](#instructions)
- [Troubleshooting](#troubleshooting)
- [Supporting Materials](#supporting-materials)

## Intro

In the next part of this course, you'll use a virtual machine (VM) to run an SQL database server and a web app that uses it. The VM is a Linux server system that runs on top of your own computer. You can share files easily between your computer and the VM; and you'll be running a web service inside the VM which you'll be able to access from your regular browser.

We're using tools called [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) to install and manage the VM. You'll need to install these to do some of the exercises. The instructions on this page will help you do this.

### Conceptual overview

[This video](https://www.youtube.com/watch?v=djnqoEO2rLc) offers a conceptual overview of virtual machines and Vagrant. You don't need to watch it to proceed, but you may find it informative.

### Use a terminal

You'll be doing these exercises using a Unix-style terminal on your computer. If you are using a **Mac or Linux** system, your regular terminal program will do just fine. On **Windows**, we recommend using the **Git Bash** terminal that comes with the Git software. If you don't already have Git installed, download Git from [git-scm.com](https://git-scm.com/downloads).

For a refresher on using the Unix shell, look back at [our Shell Workshop](https://www.udacity.com/course/ud206).

If you'd like to learn more about Git, take a look at [our course about Git](https://www.udacity.com/course/ud123).

## Installation

### Install VirtualBox

VirtualBox is the software that actually runs the virtual machine. [You can download it from virtualbox.org, here.](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) Install the _platform package_ for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it; Vagrant will do that.

Currently (October 2017), the supported version of VirtualBox to install is version 5.1. Newer versions do not work with the current release of Vagrant.

**Ubuntu users:** If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center instead. Due to a reported bug, installing VirtualBox from the site may uninstall other software you need.

### Install Vagrant

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. [Download it from vagrantup.com.](https://www.vagrantup.com/downloads.html) Install the version for your operating system.

**Windows users:** The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

![vagrant --version](https://d17h27t6h515a5.cloudfront.net/topher/2016/December/584881ee_screen-shot-2016-12-07-at-13.40.43/screen-shot-2016-12-07-at-13.40.43.png)

_If Vagrant is successfully installed, you will be able to run_ `vagrant --version`
_in your terminal to see the version number._
_The shell prompt in your terminal may differ. Here, the_ `$` _sign is the shell prompt._

### Download the VM configuration

Use Github to fork and clone, or download, the repository [https://github.com/udacity/fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm).

You will end up with a new directory containing the VM files. Change to this directory in your terminal with `cd`. Inside, you will find another directory called **vagrant**. Change directory to the **vagrant** directory:

![vagrant-directory](https://d17h27t6h515a5.cloudfront.net/topher/2016/December/58487f12_screen-shot-2016-12-07-at-13.28.31/screen-shot-2016-12-07-at-13.28.31.png)

_Navigating to the FSND-Virtual-Machine directory and listing the files in it._
_This picture was taken on a Mac, but the commands will look the same on Git Bash on Windows._

## Instructions

### Start the virtual machine

From your terminal, inside the **vagrant** subdirectory, run the command `vagrant up`. This will cause Vagrant to download the Linux operating system and install it. This may take quite a while (many minutes) depending on how fast your Internet connection is.

![vagrant-up-start](https://d17h27t6h515a5.cloudfront.net/topher/2016/December/58488603_screen-shot-2016-12-07-at-13.57.50/screen-shot-2016-12-07-at-13.57.50.png)

_Starting the Ubuntu Linux installation with `vagrant up`._
_This screenshot shows just the beginning of many, many pages of output in a lot of colors._

When `vagrant up` is finished running, you will get your shell prompt back. At this point, you can run `vagrant ssh` to log in to your newly installed Linux VM!

![linux-vm-login](https://d17h27t6h515a5.cloudfront.net/topher/2016/December/58488962_screen-shot-2016-12-07-at-14.12.29/screen-shot-2016-12-07-at-14.12.29.png)

_Logging into the Linux VM with `vagrant ssh`._

### Logged in

If you are now looking at a shell prompt that starts with the word `vagrant` (as in the above screenshot), congratulations — you've gotten logged into your Linux VM.

If not, take a look at the [Troubleshooting](#troubleshooting) section below.

### The files for this course

Inside the VM, change directory to `/vagrant` and look around with `ls`.

The files you see here are the same as the ones in the `vagrant` subdirectory on your computer (where you started Vagrant from). Any file you create in one will be automatically shared to the other. This means that you can edit code in your favorite text editor, and run it inside the VM.

Files in the VM's `/vagrant` directory are shared with the `vagrant` folder on your computer. But other data inside the VM is not. For instance, the PostgreSQL database itself lives only inside the VM.

### Running the database

The PostgreSQL database server will automatically be started inside the VM. You can use the `psql` command-line tool to access it and run SQL statements:

![linux-vm-PostgreSQL](https://d17h27t6h515a5.cloudfront.net/topher/2016/December/58489186_screen-shot-2016-12-07-at-14.46.25/screen-shot-2016-12-07-at-14.46.25.png)

_Running `psql`, the PostgreSQL command interface, inside the VM._

### Logging out and in

If you type `exit` (or `Ctrl-D`) at the shell prompt inside the VM, you will be logged out, and put back into your host computer's shell. To log back in, make sure you're in the same directory and type `vagrant ssh` again.

If you reboot your computer, you will need to run `vagrant up` to restart the VM.

## Troubleshooting

### I'm not sure if it worked

If you can type `vagrant ssh` and log into your VM, then it worked! It's normal for the `vagrant up` process to display a lot of text in many colors, including sometimes scary-looking messages in red, green, and purple. If you get your shell prompt back at the end, and you can log in, it should be OK.

### `vagrant up` is taking a long time

Because it's downloading a whole Linux operating system from the Internet.

### I'm on Windows, and when I run `vagrant ssh`, I don't get a shell prompt

Some versions of Windows and Vagrant have a problem communicating the right settings for the terminal. There is a workaround: Instead of `vagrant ssh`, run the command `winpty vagrant ssh` instead.

### I'm on Windows and getting an error about virtualization

Sometimes other virtualization programs such as Docker or Hyper-V can interfere with VirtualBox. Try shutting these other programs down first.

In addition, some Windows PCs have settings in the BIOS or UEFI (firmware) or in the operating system that disable the use of virtualization. To change this, you may need to reboot your computer and access the firmware settings. [A web search](https://www.google.com/search?q=enable%20virtualization%20windows%2010) can help you find the settings for your computer and operating system. Unfortunately there are so many different versions of Windows and PCs that we can't offer a simple guide to doing this.

### Why are we using a VM, it seems complicated

It is complicated. In this case, the point of it is to be able to offer the same software (Linux and PostgreSQL) regardless of what kind of computer you're running on.

### I got some other error message

If you're getting a specific textual error message, try looking it up on your favorite search engine. If that doesn't help, take a screenshot and post it to the discussion forums, along with as much detail as you can provide about the process you went through to get there.

### If all else fails, try an older version

Udacity mentors have noticed that some newer versions of Vagrant don't work on all operating systems. Version 1.9.2 is reported to be stabler on some systems, and version 1.9.1 is the supported version on Ubuntu 17.04. You can download older versions of Vagrant from [the Vagrant releases index](https://releases.hashicorp.com/vagrant/).

## Supporting Materials

[Virtual machine repository on GitHub](https://github.com/udacity/fullstack-nanodegree-vm)

[(Back to TOC)](#table-of-contents)