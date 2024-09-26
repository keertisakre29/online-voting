# import the necessary packages
from flask import Flask, render_template, redirect, url_for, request,session,Response
from werkzeug import secure_filename
import os
import cv2
from utils import *
import pandas as pd
from playsound import playsound
from sms import *
import random

fname=''
lname=''
adhar=''
voter=''
name=''
contact = ''
otp=''

app = Flask(__name__)

app.secret_key = '1234'
app.config["CACHE_TYPE"] = "null"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/', methods=['GET', 'POST'])
def landing():
	return render_template('home.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
	return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	global name
	global adhar
	global voter
	global contact
	error = ""

	if request.method=='POST':
		name = request.form['name']
		adhar = request.form['adhar']
		voter = request.form['voter']
		contact = request.form['contact']
		#fp = request.form['fingerprint']
		#print(fp)


		if(len(adhar)!=12):
			error += "Adhar number Invalid  "
		if(len(voter)!=10 or voter[0:3].isalpha()==False):
			error += "Voter ID Invalid"
		if(error == ""):	
			df = pd.read_csv('aadhar DB.csv')
			#print(df)
			df1 = pd.read_csv('Voter DB.csv')
			#print(df1)
			count=df.iloc[:,0].astype(str).str.contains(adhar).any()
			count1=df1.iloc[:,0].astype(str).str.contains(voter).any()
			print(count,count1)

			df2 = pd.read_csv('viis.csv')
			count2 = df2.iloc[:,2].astype(str).str.contains(adhar).any()

			if(count and count1 and count2==0):		
				return redirect(url_for('register1'))
			elif(count2!=0):
				error += "This Record is Already Present in VIIS"
			else:
				error += "Adhar/Voter is not in Database"
		
	return render_template('register.html',error=error)

@app.route('/register1', methods=['GET', 'POST'])
def register1():
	global name
	global adhar
	global voter
	global contact	
	if request.method=='POST':

		img = cv2.imread('static/images/test_image.jpg')
		cv2.imwrite('dataset/'+name+'.jpg', img)

		data_list = {'name':name,'adhar':adhar,'voter':voter,'vote':0,'contact':contact}
		df = pd.DataFrame(data_list,index=[0])
		df.to_csv('viis.csv', mode='a',header=False)

		return redirect(url_for('register'))

	return render_template('register1.html',name=name,adhar= adhar,voter=voter,contact=contact)


@app.route('/input', methods=['GET', 'POST'])
def input():
	global fname
	global lname
	global adhar
	global voter
	global otp

	df = pd.read_csv('viis.csv')
		
	if request.method=='POST':
		code = int(request.form['otp'])
		face = faceRecognition()
		print(face)
		print(code)
		print(fname)
		if len(face)>0:	
			if (face[0] == fname) and code == otp:
				for i in range(len(df)):
					if(df.values[i][0]==fname):
						df.iloc[i,3] = 1
						df.to_csv('viis.csv',index=False)
						return redirect(url_for('vote'))
		else:
			return redirect(url_for('video')) 

	return render_template('input.html',fname=fname,lname=lname,adhar= adhar,voter=voter)

@app.route('/video', methods=['GET', 'POST'])
def video():
	global fname
	global lname
	global adhar
	global voter
	global contact
	global otp
	f=0
	
	df = pd.read_csv('viis.csv')
	print(df)
	print(df.values[0][0])
	print(df.iloc[:,3])

	if request.method == 'POST':
		fname = request.form['fname']
		lname = request.form['lname']
		adhar = request.form['adhar']
		voter = request.form['voter']

		for i in range(len(df)):
			if(df.values[i][0]==fname and df.iloc[i,3]==0):
				f=1
				break
		if(f==1):
			otp = random.randrange(1000,9999)
			print(otp)
			#sendSMS('+9188888888', '+91'+contact, 'OTP for Voting:'+str(otp))
			return redirect(url_for('input'))
		else:
			return render_template('video.html',error="No record Found / You have voted already")
	return render_template('video.html')

@app.route('/video_stream')
def video_stream():

	return Response(video_feed(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
	if request.method == 'POST':
		df = pd.read_csv('candidate.csv')
		vote_id = int(request.form['can'])
		vote = df._get_value(vote_id,'votes')
		df._set_value(vote_id,'votes',vote+1)
		df.to_csv('candidate.csv',index=False)
		print(df)
		playsound('vote.wav')
		return redirect(url_for('video'))

	return render_template('vote.html')

@app.route('/result', methods=['GET', 'POST'])
def result():
	error = None
	if request.method == 'POST':
		if request.form['username'] != 'admin' or request.form['password'] != 'admin':
			error = 'Invalid Credentials. Please try again.'
		else:
			df = pd.read_csv('candidate.csv')
			df.sort_values(by=['votes'], inplace=True,ascending=False)
			df.to_html('templates/vote_count.html',index=False)
			return render_template('result.html',tables=[df.to_html(classes='data')], titles=df.columns.values,index=False)

	return render_template('result.html', error=error)


# No caching at all for API endpoints.
@app.after_request
def add_header(response):
	# response.cache_control.no_store = True
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '-1'
	return response


if __name__ == '__main__' and run:
	app.run(host='0.0.0.0', debug=False)