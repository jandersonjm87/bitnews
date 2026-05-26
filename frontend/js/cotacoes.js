const API_BASE='/api';
let grafico=null,periodoAtual='7d',moedaSelecionada='bitcoin',tipoSelecionado='crypto';

const formatarBRL=(v)=>new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(v);
const formatarUSD=(v)=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',minimumFractionDigits:2,maximumFractionDigits:v<1?6:2}).format(v);
const formatarVar=(v)=>v!=null?((v>0?'+':'')+v.toFixed(2)+'%'):'--';
const classeVar=(v)=>v==null?'neutro':v>0?'positivo':'negativo';

function renderCard(c){
  const v=c.preco.variacao_24h;
  const img=c.imagem?'<img src="'+c.imagem+'" class="card-img" onerror="this.style.display=none">':'<div class="card-img-placeholder">'+c.simbolo[0]+'</div>';
  const sel=moedaSelecionada===c.id?'selected':'';
  const tipo_label=c.tipo==='crypto'?'Crypto':'Fiat';
  const var_html=v!=null?'<span class="card-variacao '+classeVar(v)+'">'+(v>0?'▲':'▼')+' '+formatarVar(v)+' hoje</span>':'';
  return '<div class="cotacao-card '+sel+'" onclick="selecionarMoeda(\''+c.id+'\',\''+c.tipo+'\')" id="card-'+c.id+'">'
    +'<div class="card-top"><div class="card-info">'+img+'<div><div class="card-nome">'+c.nome+'</div><div class="card-simbolo">'+c.simbolo+'</div></div></div>'
    +'<span class="card-tipo '+c.tipo+'">'+tipo_label+'</span></div>'
    +'<div class="card-preco-brl">'+formatarBRL(c.preco.brl)+'</div>'
    +'<div class="card-preco-usd">'+formatarUSD(c.preco.usd)+'</div>'
    +var_html+'</div>';
}

async function buscarCotacoes(){
  try{
    const res=await fetch(API_BASE+'/cotacoes/');
    const data=await res.json();
    document.getElementById('cotacoesGrid').innerHTML=data.cotacoes.map(renderCard).join('');
    document.getElementById('cotacoesUpdate').textContent='Atualizado: '+new Date().toLocaleTimeString('pt-BR');
    setStatus(true);
  }catch(e){setStatus(false);}
}

async function atualizarGrafico(){
  const sel=document.getElementById('moedaSelect');
  moedaSelecionada=sel.value;
  tipoSelecionado=sel.options[sel.selectedIndex].dataset.tipo;
  document.querySelectorAll('.cotacao-card').forEach(function(c){c.classList.remove('selected');});
  var el=document.getElementById('card-'+moedaSelecionada);
  if(el) el.classList.add('selected');
  try{
    const res=await fetch(API_BASE+'/cotacoes/historico/'+moedaSelecionada+'?periodo='+periodoAtual+'&tipo='+tipoSelecionado);
    const data=await res.json();
    const labels=data.dados.map(function(p){return new Date(p.timestamp);});
    const precos=data.dados.map(function(p){return p.preco;});
    const ctx=document.getElementById('graficoPreco').getContext('2d');
    if(grafico) grafico.destroy();
    const grad=ctx.createLinearGradient(0,0,0,300);
    grad.addColorStop(0,'rgba(247,147,26,0.35)');
    grad.addColorStop(1,'rgba(247,147,26,0)');
    grafico=new Chart(ctx,{
      type:'line',
      data:{labels:labels,datasets:[{label:moedaSelecionada,data:precos,borderColor:'#f7931a',backgroundColor:grad,borderWidth:2,pointRadius:0,pointHoverRadius:5,tension:0.4,fill:true}]},
      options:{
        responsive:true,maintainAspectRatio:false,
        interaction:{mode:'index',intersect:false},
        plugins:{legend:{display:false},tooltip:{backgroundColor:'#111620',borderColor:'#1e2840',borderWidth:1,titleColor:'#8899bb',bodyColor:'#f0f4ff',callbacks:{label:function(c){return ' '+formatarUSD(c.parsed.y);}}}},
        scales:{
          x:{type:'time',time:{unit:periodoAtual==='1d'?'hour':periodoAtual==='7d'?'day':'week',displayFormats:{hour:'HH:mm',day:'dd/MM',week:'dd/MM'}},grid:{color:'#1e2840'},ticks:{color:'#445566',font:{size:11}}},
          y:{grid:{color:'#1e2840'},ticks:{color:'#445566',font:{size:11},callback:function(v){return formatarUSD(v);}}}
        }
      }
    });
  }catch(e){console.error('Erro grafico:',e);}
}

function selecionarPeriodo(periodo,btn){
  periodoAtual=periodo;
  document.querySelectorAll('.periodo-btn').forEach(function(b){b.classList.remove('active');});
  btn.classList.add('active');
  atualizarGrafico();
}

function selecionarMoeda(id,tipo){
  moedaSelecionada=id;
  tipoSelecionado=tipo;
  document.getElementById('moedaSelect').value=id;
  atualizarGrafico();
}

async function inicializarCotacoes(){
  await buscarCotacoes();
  await atualizarGrafico();
  setInterval(buscarCotacoes,10000);
}
