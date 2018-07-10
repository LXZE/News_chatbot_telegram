require('dotenv').config()
const Telegraf = require('telegraf')
const bot = new Telegraf(process.env.telegram_bot_id)
const request = require('request')
let userTopic = {}
const headers = {
    "content-type": "application/json",
}

bot.start((ctx) => {
	ctx.reply('Hello there! you can ask me for news')
})

bot.on('text', async (ctx) => {
	if(userTopic[`${ctx.message.from.id}`] == undefined){
		userTopic[`${ctx.message.from.id}`] = ''
	}
	try{
		ctx.replyWithChatAction('typing')
		let res = await processingText(
			ctx.message.text,
			userTopic[`${ctx.message.from.id}`]
		)
		if(res['topic'] != ''){
			userTopic[`${ctx.message.from.id}`] = res['topic']
			console.log(
				`topic updated: ${ctx.message.from.id} -> ${res['topic']}`
			)
		}else if(res['type'] == 'error' && res['topic'] == ''){
			ctx.reply('Topic not told yet')
			return
		}
		ctx.reply(res.content)
	}catch(e){
		console.error(`[ERR] ${e}`)
		ctx.reply('Error on process', e)
	}
})

bot.catch((err)=>{
	console.error(err)
})

bot.startPolling()

const processingText = (text, topic) => {
	return new Promise((resolve,reject)=>{
		request({
			method: 'post',
			url: 'http://127.0.0.1:5000/chat',
			body: {text: text, topic: topic},
			headers: headers,
			json: true,
		},(err,res,body)=>{
			if(!err){
				resolve(body)
			}else{
				reject(err)
			}
		})
	}) 
}


// bot.use((ctx, next)=>{
// 	ctx.replyWithChatAction(ctx.message.chat_id, 'typing').then(()=>{
// 		return next()
// 	}).catch
// })


// const wait = () => {
// 	return new Promise((resolve, reject)=>{
// 		setTimeout(()=>{
// 			resolve()
// 		}, 2000)
// 	})
// }



// bot.use((ctx, next) => {
// 	const start = new Date()
// 	return next(ctx).then(() => {
// 		const ms = new Date() - start
// 		console.log('Response time %sms', ms)
// 	})
// })
// bot.start((ctx) => ctx.reply('Welcome!'))
// bot.help((ctx) => ctx.reply('Send me a sticker'))
// bot.on('sticker', (ctx) => ctx.reply('👍'))
// bot.hears('hi', (ctx) => ctx.reply('Hey there'))
// bot.hears(/buy/i, (ctx) => ctx.reply('Buy-buy'))

// bot.command('/oldschool', (ctx) => ctx.reply('Hello'))
// bot.command('/modern', ({ reply }) => reply('Yo'))
// bot.command('/hipster', Telegraf.reply('λ'))